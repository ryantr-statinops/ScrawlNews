import sqlite3
from pathlib import Path
from src.repositories.migrate import run_migrations


class PipelineRunRepository:
    def __init__(self, db_url: str = "sqlite:///data/scrawlnews.db"):
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        run_migrations(self.db_path)
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

    def create(self, run):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO pipeline_runs (id, status, task_id, articles_fetched, summaries_generated, telegram_sent, error, started_at, finished_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    run.id,
                    run.status,
                    getattr(run, "task_id", None),
                    getattr(run, "articles_fetched", 0),
                    getattr(run, "summaries_generated", 0),
                    getattr(run, "telegram_sent", 0),
                    getattr(run, "error", None),
                    getattr(run, "started_at", None),
                    getattr(run, "finished_at", None),
                ),
            )
            conn.commit()
            return run

    def get(self, run_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM pipeline_runs WHERE id = ?", (run_id,)).fetchone()
            return dict(row) if row else None

    def list_recent(self, limit: int = 20):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def update_status(self, run_id: str, status: str, **fields):
        set_clause = ["status = ?"]
        params = [status]
        for key, value in fields.items():
            set_clause.append(f"{key} = ?")
            params.append(value)
        set_clause_str = ", ".join(set_clause)
        params.append(run_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"UPDATE pipeline_runs SET {set_clause_str} WHERE id = ?", params)
            conn.commit()

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()
            return row[0] if row else 0
