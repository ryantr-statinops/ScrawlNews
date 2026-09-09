import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from statistics import median
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.config import settings
from src.repositories.article_repo import ArticleRepository
from src.repositories.config_repo import ConfigRepository
from src.repositories.run_repo import PipelineRunRepository
from src.repositories.summary_repo import SummaryRepository
from src.repositories.telemetry_repo import TelemetryRepository

WINDOWS = {
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "12h": timedelta(hours=12),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


@dataclass(frozen=True)
class AnalyticsPeriod:
    window: str
    timezone: str
    current_start: datetime
    current_end: datetime
    previous_start: datetime
    previous_end: datetime

    def as_dict(self) -> dict:
        return {
            "window": self.window,
            "timezone": self.timezone,
            "current": {
                "from": self.current_start.isoformat(),
                "to": self.current_end.isoformat(),
            },
            "previous": {
                "from": self.previous_start.isoformat(),
                "to": self.previous_end.isoformat(),
            },
        }


def comparison(current: float | int, previous: float | int) -> dict:
    delta = current - previous
    delta_percent = None if previous == 0 else round(delta / previous * 100, 1)
    return {
        "current": current,
        "previous": previous,
        "delta": delta,
        "delta_percent": delta_percent,
    }


def percentile(values: list[float], percentage: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * percentage + 0.5)))
    return round(ordered[index], 1)


def parse_timestamp(value: str) -> datetime:
    """Normalize SQLite timestamps to a naive UTC datetime for comparisons."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed
    return parsed.astimezone(UTC).replace(tzinfo=None)


class AnalyticsService:
    def __init__(self, db_url: str | None = None, now: datetime | None = None):
        self.db_url = db_url or settings.database_url
        self.db_path = TelemetryRepository(self.db_url).db_path
        ArticleRepository(self.db_url)
        SummaryRepository(self.db_url)
        PipelineRunRepository(self.db_url)
        self.now = (now or datetime.now(UTC)).astimezone(UTC)

    def period(self, window: str) -> AnalyticsPeriod:
        if window not in WINDOWS:
            raise ValueError(f"Unsupported analytics window: {window}")
        configured = ConfigRepository(self.db_url).get("schedule_timezone")
        timezone_name = configured or settings.schedule_timezone
        try:
            timezone = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            timezone_name = "UTC"
            timezone = ZoneInfo("UTC")
        local_end = self.now.astimezone(timezone)
        duration = WINDOWS[window]
        current_start = local_end - duration
        previous_start = current_start - duration
        return AnalyticsPeriod(
            window=window,
            timezone=timezone_name,
            current_start=current_start.astimezone(UTC).replace(tzinfo=None),
            current_end=local_end.astimezone(UTC).replace(tzinfo=None),
            previous_start=previous_start.astimezone(UTC).replace(tzinfo=None),
            previous_end=current_start.astimezone(UTC).replace(tzinfo=None),
        )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _bounds(period: AnalyticsPeriod, previous: bool = False) -> tuple[str, str]:
        start = period.previous_start if previous else period.current_start
        end = period.previous_end if previous else period.current_end
        return start.isoformat(), end.isoformat()

    @staticmethod
    def _filters(
        *,
        alias: str = "",
        category: str | None = None,
        source_id: str | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> tuple[str, list[str]]:
        prefix = f"{alias}." if alias else ""
        clauses: list[str] = []
        params: list[str] = []
        if category:
            clauses.append(f"{prefix}category = ?")
            params.append(category)
        if source_id:
            clauses.append(f"{prefix}source = ?")
            params.append(source_id)
        if provider:
            clauses.append(f"{prefix}provider = ?")
            params.append(provider)
        if model:
            clauses.append(f"{prefix}model = ?")
            params.append(model)
        return (" AND " + " AND ".join(clauses) if clauses else ""), params

    def _article_count(
        self,
        conn: sqlite3.Connection,
        period: AnalyticsPeriod,
        previous: bool,
        category: str | None,
        source_id: str | None,
    ) -> int:
        start, end = self._bounds(period, previous)
        filters, params = self._filters(category=category, source_id=source_id)
        row = conn.execute(
            "SELECT COUNT(*) FROM articles WHERE datetime(fetched_at) >= datetime(?) "
            "AND datetime(fetched_at) < datetime(?)" + filters,
            [start, end, *params],
        ).fetchone()
        return int(row[0] if row else 0)

    def _summary_coverage(
        self,
        conn: sqlite3.Connection,
        period: AnalyticsPeriod,
        previous: bool,
        category: str | None,
        source_id: str | None,
    ) -> float:
        start, end = self._bounds(period, previous)
        filters, params = self._filters(alias="a", category=category, source_id=source_id)
        row = conn.execute(
            """SELECT COUNT(*) AS total,
            SUM(CASE WHEN EXISTS (SELECT 1 FROM summaries s WHERE s.article_id = a.id)
                THEN 1 ELSE 0 END) AS summarized
            FROM articles a WHERE datetime(a.fetched_at) >= datetime(?)
            AND datetime(a.fetched_at) < datetime(?)""" + filters,
            [start, end, *params],
        ).fetchone()
        total = int(row["total"] or 0) if row else 0
        summarized = int(row["summarized"] or 0) if row else 0
        return round(summarized / total * 100, 1) if total else 0.0

    def _run_success_rate(
        self, conn: sqlite3.Connection, period: AnalyticsPeriod, previous: bool
    ) -> float:
        start, end = self._bounds(period, previous)
        row = conn.execute(
            """SELECT COUNT(*) AS total,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successful
            FROM pipeline_runs WHERE datetime(started_at) >= datetime(?)
            AND datetime(started_at) < datetime(?)
            AND status IN ('success', 'failed')""",
            (start, end),
        ).fetchone()
        total = int(row["total"] or 0) if row else 0
        successful = int(row["successful"] or 0) if row else 0
        return round(successful / total * 100, 1) if total else 0.0

    def _token_total(
        self,
        conn: sqlite3.Connection,
        period: AnalyticsPeriod,
        previous: bool,
        provider: str | None,
        model: str | None,
    ) -> int:
        start, end = self._bounds(period, previous)
        filters, params = self._filters(provider=provider, model=model)
        row = conn.execute(
            "SELECT COALESCE(SUM(total_tokens), 0) FROM llm_usage_events "
            "WHERE datetime(occurred_at) >= datetime(?) AND datetime(occurred_at) < datetime(?)"
            + filters,
            [start, end, *params],
        ).fetchone()
        return int(row[0] if row else 0)

    def overview(
        self,
        window: str = "24h",
        category: str | None = None,
        source_id: str | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> dict:
        period = self.period(window)
        with self._connect() as conn:
            article_values = [
                self._article_count(conn, period, previous, category, source_id)
                for previous in (False, True)
            ]
            coverage_values = [
                self._summary_coverage(conn, period, previous, category, source_id)
                for previous in (False, True)
            ]
            success_values = [
                self._run_success_rate(conn, period, previous) for previous in (False, True)
            ]
            token_values = [
                self._token_total(conn, period, previous, provider, model)
                for previous in (False, True)
            ]
            active_sources = []
            freshness = []
            for previous in (False, True):
                start, end = self._bounds(period, previous)
                source_filters, source_params = self._filters(
                    provider=None, model=None
                )
                source_row = conn.execute(
                    """SELECT COUNT(DISTINCT source_id) FROM source_fetch_events
                    WHERE datetime(occurred_at) >= datetime(?)
                    AND datetime(occurred_at) < datetime(?) AND status = 'success'"""
                    + source_filters,
                    [start, end, *source_params],
                ).fetchone()
                active_sources.append(int(source_row[0] if source_row else 0))
                article_filters, article_params = self._filters(
                    category=category, source_id=source_id
                )
                rows = conn.execute(
                    """SELECT COALESCE(published_at, fetched_at) AS timestamp FROM articles
                    WHERE datetime(fetched_at) >= datetime(?)
                    AND datetime(fetched_at) < datetime(?)""" + article_filters,
                    [start, end, *article_params],
                ).fetchall()
                reference = period.previous_end if previous else period.current_end
                ages = [
                    max(0.0, (reference - parse_timestamp(row[0])).total_seconds() / 60)
                    for row in rows
                    if row[0]
                ]
                freshness.append(round(median(ages), 1) if ages else 0.0)

            start, end = self._bounds(period)
            failures = conn.execute(
                "SELECT COUNT(*) FROM pipeline_runs WHERE datetime(started_at) >= datetime(?) "
                "AND datetime(started_at) < datetime(?) "
                "AND status = 'failed'",
                (start, end),
            ).fetchone()[0]
            source_errors = conn.execute(
                "SELECT COUNT(*) FROM source_fetch_events "
                "WHERE datetime(occurred_at) >= datetime(?) "
                "AND datetime(occurred_at) < datetime(?) AND status != 'success'",
                (start, end),
            ).fetchone()[0]
            llm_errors = conn.execute(
                "SELECT COUNT(*) FROM llm_usage_events "
                "WHERE datetime(occurred_at) >= datetime(?) "
                "AND datetime(occurred_at) < datetime(?) AND status != 'success'",
                (start, end),
            ).fetchone()[0]
            alerts = []
            if failures:
                alerts.append({"severity": "error", "kind": "pipeline", "count": failures})
            if source_errors:
                alerts.append({"severity": "warning", "kind": "source", "count": source_errors})
            backlog = max(0, article_values[0] - round(article_values[0] * coverage_values[0] / 100))
            if backlog:
                alerts.append({"severity": "warning", "kind": "summary_backlog", "count": backlog})
            if llm_errors:
                alerts.append({"severity": "error", "kind": "llm", "count": llm_errors})

        content = self.content(window, category, source_id)
        return {
            "period": period.as_dict(),
            "kpis": {
                "articles": comparison(*article_values),
                "active_sources": comparison(*active_sources),
                "freshness_minutes": comparison(*freshness),
                "summary_coverage": comparison(*coverage_values),
                "pipeline_success_rate": comparison(*success_values),
                "total_tokens": comparison(*token_values),
            },
            "alerts": alerts,
            "trend": content["velocity"],
            "categories": content["categories"][:6],
            "sources": content["sources"][:6],
        }

    def content(
        self,
        window: str = "24h",
        category: str | None = None,
        source_id: str | None = None,
    ) -> dict:
        period = self.period(window)
        start, end = self._bounds(period)
        previous_start, previous_end = self._bounds(period, True)
        filters, params = self._filters(category=category, source_id=source_id)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT fetched_at, COALESCE(category, 'uncategorized') category, "
                "COALESCE(source, 'unknown') source, COALESCE(published_at, fetched_at) published "
                "FROM articles WHERE datetime(fetched_at) >= datetime(?) "
                "AND datetime(fetched_at) < datetime(?)" + filters,
                [start, end, *params],
            ).fetchall()
            summary_filters, summary_params = self._filters(
                alias="a", category=category, source_id=source_id
            )
            summary_rows = conn.execute(
                """SELECT s.created_at FROM summaries s
                JOIN articles a ON a.id = s.article_id
                WHERE datetime(s.created_at) >= datetime(?)
                AND datetime(s.created_at) < datetime(?)""" + summary_filters,
                [start, end, *summary_params],
            ).fetchall()
            previous_rows = conn.execute(
                "SELECT COALESCE(category, 'uncategorized') category, "
                "COALESCE(source, 'unknown') source FROM articles "
                "WHERE datetime(fetched_at) >= datetime(?) "
                "AND datetime(fetched_at) < datetime(?)" + filters,
                [previous_start, previous_end, *params],
            ).fetchall()

        current_categories = self._count_values(rows, "category")
        previous_categories = self._count_values(previous_rows, "category")
        current_sources = self._count_values(rows, "source")
        previous_sources = self._count_values(previous_rows, "source")
        freshness = {"under_1h": 0, "1h_6h": 0, "6h_24h": 0, "over_24h": 0}
        for row in rows:
            published = parse_timestamp(row["published"])
            age_hours = max(0.0, (period.current_end - published).total_seconds() / 3600)
            bucket = (
                "under_1h" if age_hours < 1 else "1h_6h" if age_hours < 6
                else "6h_24h" if age_hours < 24 else "over_24h"
            )
            freshness[bucket] += 1
        return {
            "period": period.as_dict(),
            "velocity": self._velocity(rows, summary_rows, period),
            "categories": self._breakdown(current_categories, previous_categories, "category"),
            "sources": self._breakdown(current_sources, previous_sources, "source"),
            "diversity": len(current_sources),
            "freshness": freshness,
        }

    @staticmethod
    def _count_values(rows: list[sqlite3.Row], key: str) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for row in rows:
            counts[str(row[key])] += 1
        return counts

    @staticmethod
    def _breakdown(current: dict[str, int], previous: dict[str, int], key: str) -> list[dict]:
        return [
            {key: name, **comparison(count, previous.get(name, 0))}
            for name, count in sorted(current.items(), key=lambda item: item[1], reverse=True)
        ]

    @staticmethod
    def _velocity(
        rows: list[sqlite3.Row], summary_rows: list[sqlite3.Row], period: AnalyticsPeriod
    ) -> list[dict]:
        use_days = WINDOWS[period.window] > timedelta(days=2)
        buckets: dict[str, dict[str, int]] = defaultdict(
            lambda: {"articles": 0, "summaries": 0}
        )
        timezone = ZoneInfo(period.timezone)
        for row in rows:
            timestamp = parse_timestamp(row["fetched_at"]).replace(tzinfo=UTC)
            local = timestamp.astimezone(timezone)
            label = local.strftime("%Y-%m-%d" if use_days else "%m-%d %H:00")
            buckets[label]["articles"] += 1
        for row in summary_rows:
            timestamp = parse_timestamp(row["created_at"]).replace(tzinfo=UTC)
            local = timestamp.astimezone(timezone)
            label = local.strftime("%Y-%m-%d" if use_days else "%m-%d %H:00")
            buckets[label]["summaries"] += 1
        return [{"timestamp": key, **buckets[key]} for key in sorted(buckets)]

    def pipeline(self, window: str = "24h") -> dict:
        period = self.period(window)
        start, end = self._bounds(period)
        previous_start, previous_end = self._bounds(period, True)
        with self._connect() as conn:
            current_runs = conn.execute(
                "SELECT * FROM pipeline_runs WHERE datetime(started_at) >= datetime(?) "
                "AND datetime(started_at) < datetime(?) "
                "ORDER BY started_at DESC",
                (start, end),
            ).fetchall()
            previous_runs = conn.execute(
                "SELECT * FROM pipeline_runs WHERE datetime(started_at) >= datetime(?) "
                "AND datetime(started_at) < datetime(?)",
                (previous_start, previous_end),
            ).fetchall()
            stage_rows = conn.execute(
                "SELECT * FROM pipeline_stage_events WHERE datetime(started_at) >= datetime(?) "
                "AND datetime(started_at) < datetime(?)",
                (start, end),
            ).fetchall()
        current_success = self._success_rate(current_runs)
        previous_success = self._success_rate(previous_runs)
        durations = [self._run_duration(row) for row in current_runs if row["finished_at"]]
        previous_durations = [
            self._run_duration(row) for row in previous_runs if row["finished_at"]
        ]
        stages: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for row in stage_rows:
            stages[row["stage"]].append(row)
        stage_metrics = []
        errors: dict[tuple[str, str], int] = defaultdict(int)
        for stage, events in stages.items():
            stage_durations = [event["duration_ms"] / 1000 for event in events]
            stage_metrics.append(
                {
                    "stage": stage,
                    "calls": len(events),
                    "median_seconds": round(median(stage_durations), 1),
                    "p95_seconds": percentile(stage_durations, 0.95),
                    "items": sum(event["item_count"] or 0 for event in events),
                    "failures": sum(event["status"] != "success" for event in events),
                }
            )
            for event in events:
                if event["status"] != "success":
                    errors[(stage, event["error_class"] or "UnknownError")] += 1
        return {
            "period": period.as_dict(),
            "kpis": {
                "runs": comparison(len(current_runs), len(previous_runs)),
                "success_rate": comparison(current_success, previous_success),
                "throughput": comparison(
                    sum(row["articles_fetched"] or 0 for row in current_runs),
                    sum(row["articles_fetched"] or 0 for row in previous_runs),
                ),
                "median_duration_seconds": comparison(
                    round(median(durations), 1) if durations else 0.0,
                    round(median(previous_durations), 1) if previous_durations else 0.0,
                ),
                "p95_duration_seconds": comparison(
                    percentile(durations, 0.95), percentile(previous_durations, 0.95)
                ),
            },
            "stages": sorted(stage_metrics, key=lambda item: item["stage"]),
            "errors": [
                {"stage": stage, "error_class": error_class, "count": count}
                for (stage, error_class), count in sorted(
                    errors.items(), key=lambda item: item[1], reverse=True
                )
            ],
            "runs": [dict(row) for row in current_runs[:50]],
        }

    @staticmethod
    def _success_rate(rows: list[sqlite3.Row]) -> float:
        completed = [row for row in rows if row["status"] in ("success", "failed")]
        return (
            round(sum(row["status"] == "success" for row in completed) / len(completed) * 100, 1)
            if completed else 0.0
        )

    @staticmethod
    def _run_duration(row: sqlite3.Row) -> float:
        return max(
            0.0,
            (parse_timestamp(row["finished_at"]) - parse_timestamp(row["started_at"])).total_seconds(),
        )

    def sources(
        self, window: str = "24h", category: str | None = None, country: str | None = None
    ) -> dict:
        period = self.period(window)
        start, end = self._bounds(period)
        with self._connect() as conn:
            clauses = []
            params: list[object] = [start, end]
            if category:
                clauses.append("COALESCE(e.category, s.category) = ?")
                params.append(category)
            if country:
                clauses.append("COALESCE(e.country, s.country) = ?")
                params.append(country)
            rows = conn.execute(
                "SELECT e.*, COALESCE(e.category, s.category) AS resolved_category, "
                "COALESCE(e.country, s.country) AS resolved_country FROM source_fetch_events e "
                "LEFT JOIN sources s ON s.id = e.source_id "
                "WHERE datetime(e.occurred_at) >= datetime(?) "
                "AND datetime(e.occurred_at) < datetime(?) "
                + ("AND " + " AND ".join(clauses) + " " if clauses else "")
                + "ORDER BY e.occurred_at DESC",
                params,
            ).fetchall()
        grouped: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for row in rows:
            grouped[row["source_id"]].append(row)
        result = []
        for source_id, events in grouped.items():
            latencies = [event["latency_ms"] for event in events]
            fetched = sum(event["fetched_count"] for event in events)
            duplicates = sum(event["duplicate_count"] for event in events)
            successes = [event for event in events if event["status"] == "success"]
            result.append(
                {
                    "source_id": source_id,
                    "source_name": events[0]["source_name"],
                    "category": events[0]["resolved_category"],
                    "country": events[0]["resolved_country"],
                    "fetches": len(events),
                    "success_rate": round(len(successes) / len(events) * 100, 1),
                    "fetched": fetched,
                    "new": sum(event["new_count"] for event in events),
                    "duplicates": duplicates,
                    "duplicate_rate": round(duplicates / fetched * 100, 1) if fetched else 0.0,
                    "median_latency_ms": round(median(latencies), 1),
                    "p95_latency_ms": percentile(latencies, 0.95),
                    "last_success_at": successes[0]["occurred_at"] if successes else None,
                    "last_error": next(
                        (event["error"] for event in events if event["error"]), None
                    ),
                }
            )
        return {
            "period": period.as_dict(),
            "sources": sorted(result, key=lambda item: item["new"], reverse=True),
        }

    def ai_usage(
        self,
        window: str = "24h",
        provider: str | None = None,
        model: str | None = None,
    ) -> dict:
        period = self.period(window)
        start, end = self._bounds(period)
        previous_start, previous_end = self._bounds(period, True)
        filters, params = self._filters(provider=provider, model=model)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM llm_usage_events WHERE datetime(occurred_at) >= datetime(?) "
                "AND datetime(occurred_at) < datetime(?)"
                + filters,
                [start, end, *params],
            ).fetchall()
            previous = conn.execute(
                "SELECT * FROM llm_usage_events WHERE datetime(occurred_at) >= datetime(?) "
                "AND datetime(occurred_at) < datetime(?)"
                + filters,
                [previous_start, previous_end, *params],
            ).fetchall()
        latency = [row["latency_ms"] for row in rows]
        previous_latency = [row["latency_ms"] for row in previous]
        current_failures = sum(row["status"] != "success" for row in rows)
        previous_failures = sum(row["status"] != "success" for row in previous)
        return {
            "period": period.as_dict(),
            "kpis": {
                "total_tokens": comparison(
                    sum(row["total_tokens"] for row in rows),
                    sum(row["total_tokens"] for row in previous),
                ),
                "input_tokens": comparison(
                    sum(row["input_tokens"] for row in rows),
                    sum(row["input_tokens"] for row in previous),
                ),
                "output_tokens": comparison(
                    sum(row["output_tokens"] for row in rows),
                    sum(row["output_tokens"] for row in previous),
                ),
                "requests": comparison(len(rows), len(previous)),
                "failure_rate": comparison(
                    round(current_failures / len(rows) * 100, 1) if rows else 0.0,
                    round(previous_failures / len(previous) * 100, 1) if previous else 0.0,
                ),
                "median_latency_ms": comparison(
                    round(median(latency), 1) if latency else 0.0,
                    round(median(previous_latency), 1) if previous_latency else 0.0,
                ),
                "p95_latency_ms": comparison(
                    percentile(latency, 0.95), percentile(previous_latency, 0.95)
                ),
            },
            "trend": self._llm_trend(rows, period),
            "providers": self._usage_breakdown(rows, "provider"),
            "models": self._usage_breakdown(rows, "model"),
            "operations": self._usage_breakdown(rows, "operation"),
        }

    def drilldown(
        self,
        kind: str,
        window: str = "24h",
        category: str | None = None,
        source_id: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        run_id: str | None = None,
        operation: str | None = None,
        limit: int = 50,
    ) -> dict:
        period = self.period(window)
        start, end = self._bounds(period)
        limit = min(max(limit, 1), 100)
        with self._connect() as conn:
            if kind == "articles":
                filters, params = self._filters(category=category, source_id=source_id)
                rows = conn.execute(
                    """SELECT id, title, url, source, category, published_at, fetched_at,
                    summarized FROM articles WHERE datetime(fetched_at) >= datetime(?)
                    AND datetime(fetched_at) < datetime(?)"""
                    + filters
                    + " ORDER BY fetched_at DESC LIMIT ?",
                    [start, end, *params, limit],
                ).fetchall()
            elif kind == "runs":
                extra = " AND id = ?" if run_id else ""
                run_params: list[object] = [
                    start, end, *([run_id] if run_id else []), limit
                ]
                rows = conn.execute(
                    "SELECT * FROM pipeline_runs WHERE datetime(started_at) >= datetime(?) "
                    "AND datetime(started_at) < datetime(?)"
                    + extra
                    + " ORDER BY started_at DESC LIMIT ?",
                    run_params,
                ).fetchall()
            elif kind == "stages":
                extra = " AND run_id = ?" if run_id else ""
                stage_params: list[object] = [
                    start, end, *([run_id] if run_id else []), limit
                ]
                rows = conn.execute(
                    """SELECT * FROM pipeline_stage_events
                    WHERE datetime(started_at) >= datetime(?)
                    AND datetime(started_at) < datetime(?)"""
                    + extra
                    + " ORDER BY started_at DESC LIMIT ?",
                    stage_params,
                ).fetchall()
            elif kind == "sources":
                extra = " AND source_id = ?" if source_id else ""
                source_params: list[object] = [
                    start, end, *([source_id] if source_id else []), limit
                ]
                rows = conn.execute(
                    """SELECT * FROM source_fetch_events
                    WHERE datetime(occurred_at) >= datetime(?)
                    AND datetime(occurred_at) < datetime(?)"""
                    + extra
                    + " ORDER BY occurred_at DESC LIMIT ?",
                    source_params,
                ).fetchall()
            elif kind == "llm":
                filters, params = self._filters(provider=provider, model=model)
                extra = " AND run_id = ?" if run_id else ""
                if run_id:
                    params.append(run_id)
                if operation:
                    extra += " AND operation = ?"
                    params.append(operation)
                rows = conn.execute(
                    """SELECT id, run_id, operation, provider, model, input_tokens,
                    output_tokens, total_tokens, latency_ms, status, error, occurred_at
                    FROM llm_usage_events WHERE datetime(occurred_at) >= datetime(?)
                    AND datetime(occurred_at) < datetime(?)"""
                    + filters
                    + extra
                    + " ORDER BY occurred_at DESC LIMIT ?",
                    [start, end, *params, limit],
                ).fetchall()
            else:
                raise ValueError(f"Unsupported drilldown kind: {kind}")
        return {
            "period": period.as_dict(),
            "kind": kind,
            "records": [dict(row) for row in rows],
        }

    @staticmethod
    def _usage_breakdown(rows: list[sqlite3.Row], key: str) -> list[dict]:
        grouped: dict[str, dict[str, int]] = defaultdict(
            lambda: {"requests": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "failures": 0}
        )
        for row in rows:
            item = grouped[row[key]]
            item["requests"] += 1
            item["input_tokens"] += row["input_tokens"]
            item["output_tokens"] += row["output_tokens"]
            item["total_tokens"] += row["total_tokens"]
            item["failures"] += row["status"] != "success"
        return [
            {key: name, **values}
            for name, values in sorted(
                grouped.items(), key=lambda item: item[1]["total_tokens"], reverse=True
            )
        ]

    @staticmethod
    def _llm_trend(rows: list[sqlite3.Row], period: AnalyticsPeriod) -> list[dict]:
        use_days = WINDOWS[period.window] > timedelta(days=2)
        timezone = ZoneInfo(period.timezone)
        grouped: dict[str, dict[str, int]] = defaultdict(
            lambda: {"input_tokens": 0, "output_tokens": 0, "requests": 0}
        )
        for row in rows:
            timestamp = parse_timestamp(row["occurred_at"]).replace(tzinfo=UTC)
            local = timestamp.astimezone(timezone)
            label = local.strftime("%Y-%m-%d" if use_days else "%m-%d %H:00")
            grouped[label]["input_tokens"] += row["input_tokens"]
            grouped[label]["output_tokens"] += row["output_tokens"]
            grouped[label]["requests"] += 1
        return [{"timestamp": key, **grouped[key]} for key in sorted(grouped)]
