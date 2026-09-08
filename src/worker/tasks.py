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
from src.repositories.run_repo import PipelineRunRepository
from src.repositories.summary_repo import SummaryRepository
from src.services.messenger import MessengerService
from src.services.scrawler import ScrawlerService
from src.services.synthesizer import SynthesizerService
from src.utils.errors import MessengerError, NotFoundError, ScrawlError
from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


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
    try:
        repo.update_status(run_id, "running", finished_at=None)
        article_repo = ArticleRepository(settings.database_url)
        summary_repo = SummaryRepository(settings.database_url)
        if "article_ids" not in checkpoint:
            stage = "fetch"
            articles = asyncio.run(
                ScrawlerService().execute(
                    limit=fetch_limit or settings.fetch_limit, categories=categories
                )
            )
            articles_fetched = len(articles)
            stage = "save articles"
            new_articles = [a for a in articles if article_repo.save(a)]
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
            summaries = (
                asyncio.run(SynthesizerService().execute(new_articles)) if new_articles else []
            )
            stage = "save summaries"
            for summary in summaries:
                summary_repo.save(summary)
                summaries_generated += 1
            checkpoint["summary_ids"] = [s.id for s in summaries]
        else:
            stage = "load summaries"
            summaries = []
            for summary_id in checkpoint["summary_ids"]:
                row = summary_repo.get_by_id(summary_id)
                if row is None:
                    raise NotFoundError("Retry summary no longer exists")
                summaries.append(Summary(**row))

        if summaries and not dry_run and settings.telegram_enabled:
            stage = "deliver"
            if not asyncio.run(MessengerService().execute(summaries)):
                raise MessengerError("Messenger reported unsuccessful delivery")
            telegram_sent = 1

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
        logger.exception("Pipeline failed at %s (run %s)", stage, run_id)
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
            logger.exception("Unable to persist pipeline failure (run %s)", run_id)
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
                logger.exception("Unable to schedule pipeline retry (run %s)", run_id)
                repo.update_status(
                    run_id,
                    "failed",
                    error=f"{error}; retry scheduling failed",
                    finished_at=datetime.utcnow().isoformat(),
                )
                raise
        raise
