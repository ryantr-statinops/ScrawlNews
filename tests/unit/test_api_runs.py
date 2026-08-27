from fastapi.testclient import TestClient
from unittest.mock import patch
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
