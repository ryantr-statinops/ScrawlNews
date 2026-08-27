from fastapi import APIRouter, Query
import sqlite3
from src.config import settings
from src.repositories.article_repo import ArticleRepository

router = APIRouter()


@router.get("/api/articles")
def list_articles(q: str | None = None, source: str | None = None, summarized: int | None = None, limit: int = Query(20, le=100), offset: int = 0):
    repo = ArticleRepository(settings.database_url)
    with sqlite3.connect(repo.db_path) as conn:
        conn.row_factory = sqlite3.Row
        sql = "SELECT * FROM articles WHERE 1=1"
        params: list = []
        if q:
            sql += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        if source:
            sql += " AND source=?"
            params.append(source)
        if summarized is not None:
            sql += " AND summarized=?"
            params.append(summarized)
        sql += " ORDER BY fetched_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(sql, params).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        return {"count": total, "articles": [dict(r) for r in rows]}
