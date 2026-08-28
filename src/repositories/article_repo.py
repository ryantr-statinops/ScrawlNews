import sqlite3
from pathlib import Path


class ArticleRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    source TEXT,
                    raw_html TEXT,
                    content TEXT,
                    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    summarized INTEGER DEFAULT 0
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_fetched_at ON articles(fetched_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_summarized ON articles(summarized)")

    def cleanup_old(self, days: int = 7):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM articles WHERE fetched_at < datetime('now', ?)", (f"-{days} days",))
            conn.execute("DELETE FROM summaries WHERE created_at < datetime('now', ?)", (f"-{days} days",))
            conn.execute("DELETE FROM pipeline_runs WHERE started_at < datetime('now', ?)", (f"-{days} days",))

    def save(self, article) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO articles (id, url, title, source, raw_html, content, fetched_at, summarized) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    article.id,
                    article.url,
                    article.title,
                    getattr(article, "source", None),
                    getattr(article, "raw_html", None),
                    getattr(article, "content", None),
                    getattr(article, "fetched_at", None),
                    getattr(article, "summarized", 0),
                ),
            )
            conn.commit()
            return cur.rowcount > 0

    def exists(self, url: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT id FROM articles WHERE url = ?", (url,)).fetchone()
            return row is not None

    def get_by_id(self, article_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
            return dict(row) if row else None

    def get_unsummarized(self, limit: int = 20):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM articles WHERE summarized = 0 ORDER BY fetched_at ASC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def mark_summarized(self, article_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE articles SET summarized = 1 WHERE id = ?", (article_id,))
            conn.commit()

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM articles").fetchone()
            return row[0] if row else 0

    def get_recent(self, days: int = 7, limit: int = 100):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM articles WHERE fetched_at >= datetime('now', ?) ORDER BY fetched_at DESC LIMIT ?",
                (f"-{days} days", limit),
            ).fetchall()
            return [dict(r) for r in rows]
