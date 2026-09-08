import sqlite3

from fastapi import APIRouter

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


@router.post("/api/runs")
def trigger_run(
    fetch_limit: int | None = None,
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
