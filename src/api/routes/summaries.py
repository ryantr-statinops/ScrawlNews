import sqlite3

from fastapi import APIRouter, Query

from src.config import settings
from src.repositories.summary_repo import SummaryRepository

router = APIRouter()


@router.get("/api/summaries")
def list_summaries(article_id: str | None = None, limit: int = Query(20, le=100)):
    repo = SummaryRepository(settings.database_url)
    with sqlite3.connect(repo.db_path) as conn:
        conn.row_factory = sqlite3.Row
        sql = "SELECT * FROM summaries WHERE 1=1"
        params: list = []
        if article_id:
            sql += " AND article_id=?"
            params.append(article_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0]
        return {"count": total, "summaries": [dict(r) for r in rows]}


@router.get("/api/summaries/{summary_id}")
def get_summary(summary_id: str):
    repo = SummaryRepository(settings.database_url)
    with sqlite3.connect(repo.db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM summaries WHERE id=?", (summary_id,)).fetchone()
        if not row:
            return {"error": "not found"}
        return dict(row)
