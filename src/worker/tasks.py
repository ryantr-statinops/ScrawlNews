import asyncio
import logging
import uuid
from datetime import datetime

from celery.exceptions import Retry

from src.config import settings
from src.models.article import Article
from src.models.run import PipelineRun
from src.models.summary import Summary
from src.repositories.article_repo import ArticleRepository
from src.repositories.digest_repo import DigestRepository
from src.repositories.run_repo import PipelineRunRepository
from src.repositories.summary_repo import SummaryRepository
from src.repositories.telemetry_repo import TelemetryRepository
from src.services.digest_service import DigestService
from src.services.messenger import MessengerService
from src.services.scrawler import ScrawlerService
from src.services.synthesizer import SynthesizerService
from src.utils.errors import MessengerError, NotFoundError, ScrawlError
from src.utils.telemetry import track_stage
from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


def _record_source_events(
    telemetry: TelemetryRepository,
    scrawler: ScrawlerService,
    run_id: str,
    new_articles: list[Article],
) -> None:
    for source_event in getattr(scrawler, "fetch_events", []):
        event_urls = set(source_event.get("article_urls", []))
        new_count = sum(article.url in event_urls for article in new_articles)
        stored_event = {
            key: value for key, value in source_event.items() if key != "article_urls"
        }
        try:
            telemetry.record_source_fetch(
                run_id=run_id,
                **stored_event,
                new_count=new_count,
                duplicate_count=max(0, source_event["fetched_count"] - new_count),
            )
        except Exception:
            logger.warning("Unable to record source fetch telemetry", exc_info=True)


@celery_app.task(bind=True, max_retries=3, name="pipeline.run")
def pipeline_run(
    self,
    fetch_limit: int | None = None,
    dry_run: bool = False,
    categories: list[str] | None = None,
    *,
    _checkpoint: dict | None = None,
):
    checkpoint = dict(_checkpoint or {})
    run_id = checkpoint.setdefault("run_id", self.request.id or str(uuid.uuid4()))
    repo = PipelineRunRepository(settings.database_url)
    telemetry = TelemetryRepository(settings.database_url)
    try:
        telemetry.cleanup(30)
    except Exception:
        logger.warning("Unable to clean expired analytics telemetry", exc_info=True)
    if _checkpoint is None:
        repo.create(
            PipelineRun(
                id=run_id, status="running", task_id=self.request.id, started_at=datetime.utcnow()
            )
        )
        articles_fetched = summaries_generated = 0
    else:
        run = repo.get(run_id)
        if run is None:
            raise NotFoundError("Retry run no longer exists")
        articles_fetched = run["articles_fetched"]
        summaries_generated = run["summaries_generated"]

    telegram_sent = 0
    stage = "initialize"
    scrawler: ScrawlerService | None = None
    source_events_recorded = False
    try:
        repo.update_status(run_id, "running", finished_at=None)
        article_repo = ArticleRepository(settings.database_url)
        summary_repo = SummaryRepository(settings.database_url)
        new_articles: list[Article] = []
        if "article_ids" not in checkpoint:
            stage = "fetch"
            with track_stage(telemetry, run_id, stage) as event:
                scrawler = ScrawlerService()
                articles = asyncio.run(
                    scrawler.execute(
                        limit=fetch_limit or settings.fetch_limit, categories=categories
                    )
                )
                event["item_count"] = len(articles)
            articles_fetched = len(articles)
            stage = "save articles"
            with track_stage(telemetry, run_id, stage) as event:
                new_articles = [a for a in articles if article_repo.save(a)]
                event["item_count"] = len(new_articles)
            _record_source_events(telemetry, scrawler, run_id, new_articles)
            source_events_recorded = True
            checkpoint["article_ids"] = [a.id for a in new_articles]
        elif "summary_ids" not in checkpoint:
            stage = "load articles"
            new_articles = []
            for article_id in checkpoint["article_ids"]:
                row = article_repo.get_by_id(article_id)
                if row is None:
                    raise NotFoundError("Retry article no longer exists")
                new_articles.append(Article(**row))

        if "summary_ids" not in checkpoint:
            stage = "synthesize"
            with track_stage(telemetry, run_id, stage) as event:
                summaries = (
                    asyncio.run(SynthesizerService().execute(new_articles, run_id=run_id))
                    if new_articles
                    else []
                )
                event["item_count"] = len(summaries)
            stage = "save summaries"
            with track_stage(telemetry, run_id, stage) as event:
                for summary in summaries:
                    summary_repo.save(summary)
                    article_repo.mark_summarized(summary.article_id)
                    summaries_generated += 1
                event["item_count"] = len(summaries)
            checkpoint["summary_ids"] = [s.id for s in summaries]
        else:
            stage = "load summaries"
            summaries = []
            for summary_id in checkpoint["summary_ids"]:
                row = summary_repo.get_by_id(summary_id)
                if row is None:
                    raise NotFoundError("Retry summary no longer exists")
                summaries.append(Summary(**row))
            for article_id in checkpoint["article_ids"]:
                row = article_repo.get_by_id(article_id)
                if row is not None:
                    new_articles.append(Article(**row))

        if "digest_ids" not in checkpoint:
            stage = "digest"
            with track_stage(telemetry, run_id, stage) as event:
                digest_repo = DigestRepository(settings.database_url)
                digest_ids: list[str] = []
                by_category: dict[str, list[Article]] = {}
                for article in new_articles:
                    by_category.setdefault(article.category or "uncategorized", []).append(article)
                summaries_by_article = {summary.article_id: summary for summary in summaries}
                for category, category_articles in by_category.items():
                    category_summaries = [
                        summaries_by_article[article.id]
                        for article in category_articles
                        if article.id in summaries_by_article
                    ]
                    digest = asyncio.run(
                        DigestService().execute(
                            category, category_articles, category_summaries, run_id=run_id
                        )
                    )
                    digest_repo.save(digest, [article.id for article in category_articles])
                    digest_ids.append(digest.id)
                event["item_count"] = len(digest_ids)
            checkpoint["digest_ids"] = digest_ids

        if summaries and not dry_run and settings.telegram_enabled:
            stage = "deliver"
            with track_stage(telemetry, run_id, stage) as event:
                if not asyncio.run(MessengerService().execute(summaries)):
                    raise MessengerError("Messenger reported unsuccessful delivery")
                telegram_sent = 1
                event["item_count"] = len(summaries)

        stage = "finish"
        repo.update_status(
            run_id,
            "success",
            articles_fetched=articles_fetched,
            summaries_generated=summaries_generated,
            telegram_sent=telegram_sent,
            error=None,
            finished_at=datetime.utcnow().isoformat(),
        )
        return {
            "status": "success",
            "run_id": run_id,
            "articles_fetched": articles_fetched,
            "summaries_generated": summaries_generated,
        }
    except Exception as exc:
        if scrawler is not None and not source_events_recorded:
            _record_source_events(telemetry, scrawler, run_id, [])
        logger.exception(
            "Pipeline failed", extra={"run_id": run_id, "stage": stage}
        )
        retryable = (
            isinstance(exc, ScrawlError)
            and exc.retryable
            and self.request.retries < self.max_retries
            and not self.request.called_directly
        )
        message = (
            exc.public_message if isinstance(exc, ScrawlError) else "Unexpected pipeline failure"
        )
        # Run errors are exposed by the API; keep provider details only in internal logs.
        error = f"{stage}: {type(exc).__name__}: {message}"
        retry_note = (
            f" (retry {self.request.retries + 1}/{self.max_retries} pending)" if retryable else ""
        )
        try:
            repo.update_status(
                run_id,
                "running" if retryable else "failed",
                error=error + retry_note,
                articles_fetched=articles_fetched,
                summaries_generated=summaries_generated,
                telegram_sent=telegram_sent,
                finished_at=None if retryable else datetime.utcnow().isoformat(),
            )
        except Exception as state_error:
            logger.exception(
                "Unable to persist pipeline failure", extra={"run_id": run_id, "stage": stage}
            )
            raise exc from state_error
        if retryable:
            try:
                # IDs resume completed stages without re-fetching or losing saved delivery work.
                raise self.retry(
                    exc=exc,
                    countdown=2**self.request.retries,
                    args=(),
                    kwargs={
                        "fetch_limit": fetch_limit,
                        "dry_run": dry_run,
                        "categories": categories,
                        "_checkpoint": checkpoint,
                    },
                )
            except Retry:
                raise
            except Exception:
                logger.exception(
                    "Unable to schedule pipeline retry",
                    extra={"run_id": run_id, "stage": stage},
                )
                repo.update_status(
                    run_id,
                    "failed",
                    error=f"{error}; retry scheduling failed",
                    finished_at=datetime.utcnow().isoformat(),
                )
                raise
        raise
