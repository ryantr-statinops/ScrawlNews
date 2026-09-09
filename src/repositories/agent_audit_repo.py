"""SQLite persistence for Agent v1 audit events."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.repositories.migrate import run_migrations


class AgentAuditRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        run_migrations(self.db_path)

    def record(self, correlation_id: str, phase: str, status: str, message: str) -> int:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO agent_audit_events
                    (correlation_id, phase, status, message)
                VALUES (?, ?, ?, ?)
                """,
                (correlation_id, phase, status, message),
            )
            connection.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Unable to retrieve audit event id")
            return cursor.lastrowid

    def list_for_correlation(self, correlation_id: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, correlation_id, phase, status, message, created_at
                FROM agent_audit_events
                WHERE correlation_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (correlation_id,),
            ).fetchall()
            return [dict(row) for row in rows]
