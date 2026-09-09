import sqlite3
from pathlib import Path

from src.models.source import NewsSource
from src.repositories.migrate import run_migrations


class NewsSourceRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        run_migrations(self.db_path)

    def list(self, query: str | None = None, enabled: bool | None = None) -> list[dict]:
        sql = "SELECT * FROM sources WHERE 1=1"
        params: list = []
        if query:
            sql += " AND (name LIKE ? OR url LIKE ? OR category LIKE ?)"
            term = f"%{query}%"
            params.extend([term, term, term])
        if enabled is not None:
            sql += " AND enabled = ?"
            params.append(int(enabled))
        sql += " ORDER BY name"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def get(self, source_id: str) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
            return dict(row) if row else None

    def save(self, source: NewsSource) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO sources
                (id, name, url, category, country, city, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name, url=excluded.url,
                category=excluded.category, country=excluded.country, city=excluded.city,
                enabled=excluded.enabled""",
                (source.id, source.name, source.url, source.category, source.country,
                 source.city, source.enabled),
            )
            conn.commit()
        return self.get(source.id) or {}

    def update_status(self, source_id: str, status: str, error: str | None = None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE sources SET last_status=?, last_error=?, last_checked_at=CURRENT_TIMESTAMP WHERE id=?",
                (status, error, source_id),
            )
            conn.commit()

    def delete(self, source_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
            conn.commit()
            return cur.rowcount > 0
