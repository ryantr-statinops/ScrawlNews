import sqlite3
from datetime import datetime

ALLOWED_HOT_RELOAD_KEYS = {"fetch_limit", "summary_lang", "telegram_enabled", "retention_days"}


class ConfigRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")

    def get_all(self) -> dict[str, str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            return {row[0]: row[1] for row in rows}

    def get(self, key: str) -> str | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, datetime.utcnow().isoformat()),
            )
            conn.commit()

    def set_many(self, data: dict[str, str]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            for key, value in data.items():
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                    (key, value, datetime.utcnow().isoformat()),
                )
            conn.commit()

    def log_change(self, key: str, old_value: str | None, new_value: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO config_history (key, old_value, new_value, changed_at) VALUES (?, ?, ?, ?)",
                (key, old_value, new_value, datetime.utcnow().isoformat()),
            )
            conn.commit()

    def get_history(self, key: str | None = None, limit: int = 50) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if key:
                rows = conn.execute(
                    "SELECT * FROM config_history WHERE key = ? ORDER BY changed_at DESC LIMIT ?",
                    (key, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM config_history ORDER BY changed_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]
