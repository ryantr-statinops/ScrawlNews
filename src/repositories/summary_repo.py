import sqlite3
from pathlib import Path
from src.repositories.migrate import run_migrations


class SummaryRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        run_migrations(self.db_path)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS summaries (
                    id TEXT PRIMARY KEY,
                    article_id TEXT NOT NULL,
                    summary_text TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(article_id) REFERENCES articles(id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_summaries_article_id ON summaries(article_id)")

    def save(self, summary):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO summaries (id, article_id, summary_text, model_used, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    summary.id,
                    summary.article_id,
                    summary.summary_text,
                    summary.model_used,
                    getattr(summary, "created_at", None),
                ),
            )
            conn.commit()

    def get_by_id(self, summary_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM summaries WHERE id = ?", (summary_id,)).fetchone()
            return dict(row) if row else None

    def get_by_article(self, article_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM summaries WHERE article_id = ? ORDER BY created_at DESC", (article_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_recent(self, days: int = 7, limit: int = 100):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM summaries WHERE created_at >= datetime('now', ?) ORDER BY created_at DESC LIMIT ?",
                (f"-{days} days", limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM summaries").fetchone()
            return row[0] if row else 0
