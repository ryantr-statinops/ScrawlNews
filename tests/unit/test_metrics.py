import sqlite3
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client.parser import text_string_to_metric_families

from src.api.main import app


def _seed_database(path, *, runs=(), stages=()):
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE pipeline_runs (
                id TEXT PRIMARY KEY, status TEXT NOT NULL, started_at DATETIME,
                finished_at DATETIME
            );
            CREATE TABLE pipeline_stage_events (
                id INTEGER PRIMARY KEY, run_id TEXT, stage TEXT, status TEXT,
                duration_ms INTEGER, error_class TEXT, started_at DATETIME,
                finished_at DATETIME
            );
            """
        )
        connection.executemany("INSERT INTO pipeline_runs VALUES (?, ?, ?, ?)", runs)
        connection.executemany(
            "INSERT INTO pipeline_stage_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)", stages
        )


def _samples(body):
    return {
        (family.name, tuple(sorted(sample.labels.items()))): sample.value
        for family in text_string_to_metric_families(body)
        for sample in family.samples
    }


def test_metrics_exposes_retained_counts_and_duration_statistics(tmp_path, monkeypatch):
    now = datetime.now(UTC).replace(microsecond=0)
    runs = []
    for index, status in enumerate(("success", "success", "failed", "running"), start=1):
        started = now - timedelta(seconds=20)
        finished = (started + timedelta(seconds=index)).isoformat() if status != "running" else None
        runs.append((f"r{index}", status, started.isoformat(), finished))
    stages = [
        (index, "r1", "fetch", "success", index * 1000, None, now.isoformat(), now.isoformat())
        for index in range(1, 5)
    ] + [(5, "r2", "summarize", "failed", 500, "TimeoutError", now.isoformat(), now.isoformat())]
    database = tmp_path / "metrics.db"
    _seed_database(database, runs=runs, stages=stages)
    monkeypatch.setattr("src.api.routes.metrics.settings.database_url", f"sqlite:///{database}")

    response = TestClient(app).get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"] == CONTENT_TYPE_LATEST
    samples = _samples(response.text)
    assert samples[("scrawlnews_pipeline_runs", (("status", "success"),))] == 2
    assert samples[("scrawlnews_pipeline_runs", (("status", "failed"),))] == 1
    assert samples[("scrawlnews_pipeline_runs", (("status", "running"),))] == 1
    assert samples[("scrawlnews_pipeline_runs", (("status", "pending"),))] == 0
    assert samples[("scrawlnews_pipeline_run_duration_seconds", (("statistic", "median"),))] == 2
    assert samples[("scrawlnews_pipeline_run_duration_seconds", (("statistic", "p95"),))] == 3
    assert samples[("scrawlnews_pipeline_errors", (("error_class", "TimeoutError"), ("stage", "summarize")))] == 1
    assert samples[("scrawlnews_pipeline_stage_duration_seconds", (("stage", "fetch"), ("statistic", "median")))] == 2.5
    assert samples[("scrawlnews_pipeline_stage_duration_seconds", (("stage", "fetch"), ("statistic", "p95")))] == 4
    assert samples[("scrawlnews_pipeline_stage_duration_seconds", (("stage", "summarize"), ("statistic", "median")))] == 0.5


def test_metrics_empty_database_has_zero_statuses_and_no_sampleless_metrics(
    tmp_path, monkeypatch
):
    database = tmp_path / "empty.db"
    _seed_database(database)
    monkeypatch.setattr("src.api.routes.metrics.settings.database_url", f"sqlite:///{database}")

    response = TestClient(app).get("/metrics")

    assert response.status_code == 200
    samples = _samples(response.text)
    assert {labels[0][1]: value for (name, labels), value in samples.items() if name == "scrawlnews_pipeline_runs"} == {
        "pending": 0,
        "running": 0,
        "success": 0,
        "failed": 0,
    }
    assert not any(name.endswith("run_duration_seconds") for name, _ in samples)
    assert not any(name.endswith("stage_duration_seconds") for name, _ in samples)
    assert not any(name == "scrawlnews_pipeline_errors" for name, _ in samples)


def test_metrics_unavailable_database_returns_safe_503_without_creating_file(tmp_path, monkeypatch):
    database = tmp_path / "missing" / "metrics.db"
    monkeypatch.setattr("src.api.routes.metrics.settings.database_url", f"sqlite:///{database}")

    response = TestClient(app).get("/metrics")

    assert response.status_code == 503
    assert "Metrics temporarily unavailable" in response.text
    assert not database.exists()
