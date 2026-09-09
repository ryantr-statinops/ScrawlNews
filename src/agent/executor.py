"""Approved Agent v1 actions with a deliberately small allowlist."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class AgentExecutor:
    def __init__(self, database_path: str, backup_directory: str = "backups"):
        self.database_path = Path(database_path)
        self.backup_directory = Path(backup_directory)

    def execute_database_backup(self) -> Path:
        if not self.database_path.exists():
            raise FileNotFoundError(f"SQLite database does not exist: {self.database_path}")
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        target = self.backup_directory / f"{self.database_path.stem}-{timestamp}.db"
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as source, sqlite3.connect(target) as backup:
            source.backup(backup)
        return target
