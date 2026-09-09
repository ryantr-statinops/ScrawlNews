import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from src.repositories.migrate import run_migrations


class TelemetryRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        run_migrations(self.db_path)

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).replace(tzinfo=None).isoformat()

    def record_stage(self, **values) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """INSERT INTO pipeline_stage_events
                (run_id, stage, status, duration_ms, item_count, error_class, started_at, finished_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    values["run_id"], values["stage"], values["status"],
                    values.get("duration_ms", 0), values.get("item_count"),
                    values.get("error_class"), values.get("started_at", self._now()),
                    values.get("finished_at", self._now()),
                ),
            )
            conn.commit()
            return int(cursor.lastrowid or 0)

    def record_source_fetch(self, **values) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """INSERT INTO source_fetch_events
                (run_id, source_id, source_name, status, fetched_count, new_count,
                 duplicate_count, latency_ms, error, occurred_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    values.get("run_id"), values["source_id"], values["source_name"],
                    values["status"], values.get("fetched_count", 0),
                    values.get("new_count", 0), values.get("duplicate_count", 0),
                    values.get("latency_ms", 0), values.get("error"),
                    values.get("occurred_at", self._now()),
                ),
            )
            conn.commit()
            return int(cursor.lastrowid or 0)

    def record_llm_usage(self, **values) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """INSERT INTO llm_usage_events
                (run_id, operation, provider, model, input_tokens, output_tokens,
                 total_tokens, latency_ms, status, error, occurred_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    values.get("run_id"), values["operation"], values["provider"],
                    values["model"], values.get("input_tokens", 0),
                    values.get("output_tokens", 0), values.get("total_tokens", 0),
                    values.get("latency_ms", 0), values["status"], values.get("error"),
                    values.get("occurred_at", self._now()),
                ),
            )
            conn.commit()
            return int(cursor.lastrowid or 0)

    def cleanup(self, days: int = 30) -> int:
        removed = 0
        with sqlite3.connect(self.db_path) as conn:
            for table, column in (
                ("pipeline_stage_events", "started_at"),
                ("source_fetch_events", "occurred_at"),
                ("llm_usage_events", "occurred_at"),
            ):
                cursor = conn.execute(
                    f"DELETE FROM {table} WHERE {column} < datetime('now', ?)",
                    (f"-{days} days",),
                )
                removed += cursor.rowcount
            conn.commit()
        return removed
