import sqlite3
from pathlib import Path

from src.models.digest import Digest
from src.repositories.migrate import run_migrations


class DigestRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        run_migrations(self.db_path)

    def save(self, digest: Digest, article_ids: list[str]) -> dict:
        created_at = digest.created_at.isoformat() if digest.created_at else None
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO digests
                (id, category, title, digest_text, article_count, model_used, status, error, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (digest.id, digest.category, digest.title, digest.digest_text,
                 digest.article_count, digest.model_used, digest.status, digest.error, created_at),
            )
            conn.execute("DELETE FROM digest_articles WHERE digest_id = ?", (digest.id,))
            conn.executemany(
                "INSERT OR IGNORE INTO digest_articles (digest_id, article_id) VALUES (?, ?)",
                [(digest.id, article_id) for article_id in article_ids],
            )
            conn.commit()
        return self.get(digest.id) or {}

    def get(self, digest_id: str) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM digests WHERE id = ?", (digest_id,)).fetchone()
            return dict(row) if row else None

    def list_recent(self, category: str | None = None, limit: int = 20) -> list[dict]:
        sql = "SELECT * FROM digests"
        params: list = []
        if category:
            sql += " WHERE category = ?"
            params.append(category)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def articles(self, digest_id: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """SELECT a.* FROM articles a JOIN digest_articles da ON da.article_id = a.id
                WHERE da.digest_id = ? ORDER BY a.published_at DESC, a.fetched_at DESC""",
                (digest_id,),
            ).fetchall()
            return [dict(row) for row in rows]
