from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.config import settings
from src.models.run import PipelineRun
from src.repositories.run_repo import PipelineRunRepository

client = TestClient(app)


def time_plus_seconds(base: datetime, seconds: int) -> datetime:
    return base + timedelta(seconds=seconds)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_trigger_run():
    with patch("src.api.routes.runs.pipeline_run.delay") as mock:
        mock.return_value.id = "task123"
        r = client.post("/api/runs")
        assert r.status_code == 200
        assert r.json()["task_id"] == "task123"


def test_trigger_run_with_fetch_limit():
    with patch("src.api.routes.runs.pipeline_run.delay") as mock:
        mock.return_value.id = "task123"
        r = client.post("/api/runs?fetch_limit=50")
        assert r.status_code == 200
        mock.assert_called_once_with(50, False, None)


@pytest.mark.parametrize("fetch_limit", [0, 101])
def test_trigger_run_rejects_out_of_range_fetch_limit(fetch_limit: int):
    r = client.post(f"/api/runs?fetch_limit={fetch_limit}")
    assert r.status_code == 422


def test_trigger_run_with_categories():
    with patch("src.api.routes.runs.pipeline_run.delay") as mock:
        mock.return_value.id = "task123"
        r = client.post("/api/runs?categories=tech,business")
        assert r.status_code == 200
        mock.assert_called_once_with(None, False, ["tech", "business"])


def test_list_runs():
    r = client.get("/api/runs")
    assert r.status_code == 200
    data = r.json()
    assert "runs" in data
    assert isinstance(data["runs"], list)


def test_get_task_status():
    with patch("src.worker.celery_app.celery_app.AsyncResult") as mock:
        mock.return_value.status = "SUCCESS"
        mock.return_value.result = {"status": "success"}
        r = client.get("/api/tasks/task123")
        assert r.status_code == 200
        assert r.json()["status"] == "SUCCESS"


def test_get_task_not_found():
    with patch("src.worker.celery_app.celery_app.AsyncResult") as mock:
        mock.return_value.status = "PENDING"
        r = client.get("/api/tasks/nonexistent")
        assert r.status_code == 200


def test_runs_summary_empty():
    r = client.get("/api/runs/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_runs"] == 0
    assert data["successful_runs"] == 0
    assert data["failed_runs"] == 0
    assert data["success_rate"] == 0.0


def test_runs_summary_with_runs():
    started = datetime.utcnow()
    repo = PipelineRunRepository(settings.database_url)
    repo.create(
        PipelineRun(
            id="r1",
            status="success",
            articles_fetched=10,
            summaries_generated=5,
            telegram_sent=1,
            started_at=started,
            finished_at=time_plus_seconds(started, 30),
        )
    )
    repo.create(
        PipelineRun(
            id="r2",
            status="failed",
            articles_fetched=3,
            summaries_generated=0,
            telegram_sent=0,
            started_at=started,
            finished_at=time_plus_seconds(started, 60),
        )
    )
    repo.create(
        PipelineRun(
            id="r3",
            status="success",
            articles_fetched=5,
            summaries_generated=2,
            started_at=started,
            finished_at=time_plus_seconds(started, 45),
        )
    )
    r = client.get("/api/runs/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_runs"] == 3
    assert data["successful_runs"] == 2
    assert data["failed_runs"] == 1
    assert data["success_rate"] == pytest.approx(66.7, abs=0.1)
    assert data["articles_fetched"] == 18
    assert data["avg_duration_s"] == pytest.approx(45.0, abs=0.1)
