from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


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
        mock.assert_called_once_with(50, False)


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
