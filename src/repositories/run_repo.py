import sqlite3
from pathlib import Path


class PipelineRunRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    task_id TEXT,
                    articles_fetched INTEGER DEFAULT 0,
                    summaries_generated INTEGER DEFAULT 0,
                    telegram_sent INTEGER DEFAULT 0,
                    error TEXT,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    finished_at DATETIME
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_runs_started_at ON pipeline_runs(started_at DESC)")
