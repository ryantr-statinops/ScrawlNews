import sqlite3

from fastapi import APIRouter, Query

from src.config import settings
from src.repositories.run_repo import PipelineRunRepository
from src.utils.errors import ScrawlError
from src.worker.tasks import pipeline_run

router = APIRouter()


@router.get("/api/runs")
def list_runs(limit: int = 20):
    repo = PipelineRunRepository(settings.database_url)
    with sqlite3.connect(repo.db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return {"runs": [dict(r) for r in rows]}


@router.get("/api/runs/summary")
def runs_summary(days: int = 7):
    repo = PipelineRunRepository(settings.database_url)
    with sqlite3.connect(repo.db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_runs,
                COALESCE(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END), 0) AS successful_runs,
                COALESCE(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END), 0) AS failed_runs,
                COALESCE(SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END), 0) AS running_runs,
                COALESCE(SUM(articles_fetched), 0) AS articles_fetched,
                COALESCE(SUM(summaries_generated), 0) AS summaries_generated,
                COALESCE(SUM(telegram_sent), 0) AS telegram_sent,
                AVG((julianday(finished_at) - julianday(started_at)) * 86400.0) AS avg_duration_s
            FROM pipeline_runs
            WHERE started_at >= datetime('now', ?)
            """,
            (f"-{days} days",),
        ).fetchone()
    data = dict(row) if row else {}
    data.pop("avg_duration_s", None)
    avg = float(row["avg_duration_s"]) if row and row["avg_duration_s"] is not None else None
    data["avg_duration_s"] = round(avg, 1) if avg is not None else None
    success_rate = (
        round(data["successful_runs"] / data["total_runs"] * 100, 1)
        if data.get("total_runs")
        else 0.0
    )
    data["success_rate"] = success_rate
    return data


@router.post("/api/runs")
def trigger_run(
    fetch_limit: int | None = Query(None, ge=1, le=100),
    dry_run: bool = False,
    categories: str | None = None,
):
    cats = [c.strip() for c in categories.split(",") if c.strip()] if categories else None
    task = pipeline_run.delay(fetch_limit, dry_run, cats)
    return {"task_id": task.id, "status": "pending", "run_id": task.id}


@router.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    from src.worker.celery_app import celery_app

    result = celery_app.AsyncResult(task_id)
    status = result.status
    value = result.result
    if status in {"FAILURE", "RETRY"}:
        value = {"error": value.public_message if isinstance(value, ScrawlError) else "Task failed"}
    return {"task_id": task_id, "status": status, "result": value}
