"""Prometheus metrics collected from retained pipeline data."""

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import quote

from prometheus_client import CollectorRegistry, Gauge

from src.config import settings


class ScrawlNewsCollector:
    """Collect retained SQLite pipeline data without modifying the database."""

    RUN_STATUSES = ("pending", "running", "success", "failed")

    def __init__(self, db_url: str):
        self.db_path = db_url.removeprefix("sqlite:///")

    def collect(self, registry: CollectorRegistry):
        runs_gauge = Gauge(
            "scrawlnews_pipeline_runs",
            "Pipeline runs in the retained window by status.",
            ["status"],
            registry=registry,
        )
        run_duration = Gauge(
            "scrawlnews_pipeline_run_duration_seconds",
            "Pipeline run duration statistics in seconds.",
            ["statistic"],
            registry=registry,
        )
        errors_gauge = Gauge(
            "scrawlnews_pipeline_errors",
            "Pipeline stage errors in the retained window.",
            ["stage", "error_class"],
            registry=registry,
        )
        stage_duration = Gauge(
            "scrawlnews_pipeline_stage_duration_seconds",
            "Pipeline stage duration statistics in seconds.",
            ["stage", "statistic"],
            registry=registry,
        )

        path = Path(self.db_path).resolve()
        connection = sqlite3.connect(f"file:{quote(str(path))}?mode=ro", uri=True)
        try:
            connection.row_factory = sqlite3.Row
            cutoff = (datetime.now(UTC) - timedelta(days=settings.retention_days)).isoformat()
            runs = connection.execute(
                """SELECT status, started_at, finished_at FROM pipeline_runs
                   WHERE datetime(started_at) >= datetime(?)""",
                (cutoff,),
            ).fetchall()
            counts = {status: 0 for status in self.RUN_STATUSES}
            durations: list[float] = []
            for run in runs:
                status = str(run["status"])
                counts[status] = counts.get(status, 0) + 1
                if run["finished_at"]:
                    start = datetime.fromisoformat(str(run["started_at"]).replace("Z", "+00:00"))
                    finish = datetime.fromisoformat(str(run["finished_at"]).replace("Z", "+00:00"))
                    durations.append(max(0.0, (finish - start).total_seconds()))
            for status, count in counts.items():
                runs_gauge.labels(status=status).set(count)
            self._set_statistics(run_duration, durations)

            stages = connection.execute(
                """SELECT stage, status, duration_ms, error_class FROM pipeline_stage_events
                   WHERE datetime(started_at) >= datetime(?)""",
                (cutoff,),
            ).fetchall()
            stage_samples: dict[str, list[float]] = {}
            errors: dict[tuple[str, str], int] = {}
            for stage in stages:
                stage_name = str(stage["stage"])
                stage_samples.setdefault(stage_name, []).append(float(stage["duration_ms"]) / 1000)
                if stage["status"] == "failed" and stage["error_class"]:
                    key = (stage_name, str(stage["error_class"]))
                    errors[key] = errors.get(key, 0) + 1
            for (stage, error_class), count in errors.items():
                errors_gauge.labels(stage=stage, error_class=error_class).set(count)
            for stage, values in stage_samples.items():
                self._set_statistics(stage_duration, values, stage=stage)
        finally:
            connection.close()

    @staticmethod
    def _set_statistics(gauge: Gauge, values: list[float], stage: str | None = None):
        if not values:
            return
        ordered = sorted(values)
        median = (ordered[(len(ordered) - 1) // 2] + ordered[len(ordered) // 2]) / 2
        p95 = ordered[max(0, int(len(ordered) * 0.95 + 0.5) - 1)]
        for statistic, value in (("median", median), ("p95", p95)):
            labels = {"statistic": statistic}
            if stage is not None:
                labels["stage"] = stage
            gauge.labels(**labels).set(value)
