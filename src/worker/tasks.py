import asyncio
import uuid
from datetime import datetime

from src.config import settings
from src.repositories.article_repo import ArticleRepository
from src.repositories.run_repo import PipelineRunRepository
from src.repositories.summary_repo import SummaryRepository
from src.services.messenger import MessengerService
from src.services.scrawler import ScrawlerService
from src.services.synthesizer import SynthesizerService
from src.worker.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, name="pipeline.run")
def pipeline_run(self, fetch_limit: int | None = None, dry_run: bool = False):
    run_id = str(uuid.uuid4())
    repo = PipelineRunRepository(settings.database_url)
    # create pending
    try:
        import sqlite3

        with sqlite3.connect(repo.db_path) as conn:
            conn.execute(
                "INSERT INTO pipeline_runs (id, status, task_id, started_at) VALUES (?, ?, ?, ?)",
                (run_id, "running", self.request.id, datetime.utcnow().isoformat()),
            )
    except Exception:
        pass

    try:
        limit = fetch_limit or settings.fetch_limit
        scrawler = ScrawlerService()
        articles = asyncio.run(scrawler.execute(limit=limit))
        # save articles
        article_repo = ArticleRepository(settings.database_url)
        new_articles = []
        for a in articles:
            try:
                import sqlite3

                with sqlite3.connect(article_repo.db_path) as conn:
                    conn.execute(
                        "INSERT OR IGNORE INTO articles (id, url, title, source, content, fetched_at, summarized) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            a.id,
                            a.url,
                            a.title,
                            a.source,
                            a.content,
                            a.fetched_at.isoformat() if a.fetched_at else None,
                            0,
                        ),
                    )
                    if conn.total_changes > 0:
                        new_articles.append(a)
            except Exception:
                new_articles.append(a)

        if not new_articles:
            _finish(run_id, "success", articles_fetched=len(articles), summaries_generated=0)
            return {"status": "success", "run_id": run_id, "articles_fetched": len(articles)}

        synthesizer = SynthesizerService()
        summaries = asyncio.run(synthesizer.execute(new_articles))
        summary_repo = SummaryRepository(settings.database_url)
        for s in summaries:
            try:
                import sqlite3

                with sqlite3.connect(summary_repo.db_path) as conn:
                    conn.execute(
                        "INSERT INTO summaries (id, article_id, summary_text, model_used, created_at) VALUES (?, ?, ?, ?, ?)",
                        (
                            s.id,
                            s.article_id,
                            s.summary_text,
                            s.model_used,
                            s.created_at.isoformat() if s.created_at else None,
                        ),
                    )
            except Exception:
                pass

        telegram_sent = 0
        if not dry_run and settings.telegram_enabled:
            messenger = MessengerService()
            ok = asyncio.run(messenger.execute(summaries))
            telegram_sent = 1 if ok else 0

        _finish(
            run_id,
            "success",
            articles_fetched=len(articles),
            summaries_generated=len(summaries),
            telegram_sent=telegram_sent,
        )
        return {
            "status": "success",
            "run_id": run_id,
            "articles_fetched": len(articles),
            "summaries_generated": len(summaries),
        }
    except Exception as e:
        _finish(run_id, "failed", error=str(e))
        raise self.retry(exc=e, countdown=2**self.request.retries)


def _finish(run_id: str, status: str, **fields):
    try:
        import sqlite3

        from src.config import settings
        from src.repositories.run_repo import PipelineRunRepository

        repo = PipelineRunRepository(settings.database_url)
        sets = ", ".join([f"{k}=?" for k in fields.keys()] + ["status=?", "finished_at=?"])
        vals = list(fields.values()) + [status, datetime.utcnow().isoformat(), run_id]
        with sqlite3.connect(repo.db_path) as conn:
            conn.execute(f"UPDATE pipeline_runs SET {sets} WHERE id=?", vals)
    except Exception:
        pass
