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
