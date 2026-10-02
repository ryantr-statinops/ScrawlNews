"""Prometheus gauges derived from retained SQLite pipeline lifecycle rows."""

import math
import sqlite3
from collections import Counter, defaultdict
from collections.abc import Iterator
from pathlib import Path
from statistics import median
from urllib.parse import quote

from prometheus_client.core import GaugeMetricFamily


class ScrawlNewsCollector:
    """Scrape a read-only snapshot; never migrate or mutate the pipeline database."""

    RUN_STATUSES = ("running", "success", "failed")

    def __init__(self, db_url: str) -> None:
        self.db_path = db_url.removeprefix("sqlite:///")

    @staticmethod
    def _statistics(values: list[float]) -> tuple[float, float]:
        ordered = sorted(values)
        return median(ordered), ordered[math.ceil(0.95 * len(ordered)) - 1]

    def collect(self) -> Iterator[GaugeMetricFamily]:
        path = Path(self.db_path).resolve()
        with sqlite3.connect(f"file:{quote(str(path))}?mode=ro", uri=True) as connection:
            connection.row_factory = sqlite3.Row
            runs = connection.execute(
                "SELECT status, started_at, finished_at FROM pipeline_runs"
            ).fetchall()
            stages = connection.execute(
                "SELECT stage, status, duration_ms, error_class FROM pipeline_stage_events"
            ).fetchall()

        counts = Counter(row["status"] for row in runs)
        run_count = GaugeMetricFamily(
            "scrawlnews_pipeline_runs",
            "Pipeline runs by status in the retained SQLite window (not a cumulative counter).",
            labels=["status"],
        )
        for status in self.RUN_STATUSES:
            run_count.add_metric([status], counts[status])
        yield run_count

        from datetime import datetime

        run_durations = [
            max(
                0.0,
                (
                    datetime.fromisoformat(row["finished_at"].replace("Z", "+00:00"))
                    - datetime.fromisoformat(row["started_at"].replace("Z", "+00:00"))
                ).total_seconds(),
            )
            for row in runs
            if row["status"] in {"success", "failed"} and row["finished_at"]
        ]
        if run_durations:
            durations = GaugeMetricFamily(
                "scrawlnews_pipeline_run_duration_seconds",
                "Terminal run duration in seconds in the retained SQLite window (not cumulative).",
                labels=["stat"],
            )
            for stat, value in zip(("median", "p95"), self._statistics(run_durations)):
                durations.add_metric([stat], value)
            yield durations

        errors: Counter[tuple[str, str]] = Counter()
        stage_durations: dict[str, list[float]] = defaultdict(list)
        for row in stages:
            stage = str(row["stage"])
            if row["status"] != "success":
                errors[(stage, str(row["error_class"] or "unknown"))] += 1
            if row["duration_ms"] is not None:
                stage_durations[stage].append(float(row["duration_ms"]) / 1000)

        if errors:
            error_counts = GaugeMetricFamily(
                "scrawlnews_pipeline_errors",
                "Stage errors in the retained SQLite window (not a cumulative counter).",
                labels=["stage", "error_class"],
            )
            for (stage, error_class), count in sorted(errors.items()):
                error_counts.add_metric([stage, error_class], count)
            yield error_counts

        if stage_durations:
            durations = GaugeMetricFamily(
                "scrawlnews_pipeline_stage_duration_seconds",
                "Stage duration in seconds in the retained SQLite window (not cumulative).",
                labels=["stage", "stat"],
            )
            for stage, values in sorted(stage_durations.items()):
                for stat, value in zip(("median", "p95"), self._statistics(values)):
                    durations.add_metric([stage, stat], value)
            yield durations
