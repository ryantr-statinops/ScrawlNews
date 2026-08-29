import sqlite3
from pathlib import Path


SCHEMA_VERSION = 2

MIGRATIONS = {
    1: """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """,
    2: """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS config_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT NOT NULL,
        changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_config_history_key ON config_history(key);
    CREATE INDEX IF NOT EXISTS idx_config_history_changed_at ON config_history(changed_at DESC)
    """,
}


def run_migrations(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        row = conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        current_version = row[0] if row and row[0] is not None else 0
        for version in range(current_version + 1, SCHEMA_VERSION + 1):
            if version in MIGRATIONS:
                conn.executescript(MIGRATIONS[version])
                conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
                conn.commit()
