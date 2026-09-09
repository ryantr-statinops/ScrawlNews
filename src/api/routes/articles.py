import sqlite3
from datetime import UTC, datetime

from fastapi import APIRouter, Query

from src.config import settings
from src.repositories.article_repo import ArticleRepository

router = APIRouter()


@router.get("/api/articles")
def list_articles(
    q: str | None = None,
    source: str | None = None,
    category: str | None = None,
    summarized: int | None = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    from_: datetime | None = Query(None, alias="from"),
    to: datetime | None = Query(None),
):
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
        if category:
            sql += " AND category=?"
            params.append(category)
        if summarized is not None:
            sql += " AND summarized=?"
            params.append(summarized)
        if from_:
            sql += " AND COALESCE(published_at, fetched_at) >= ?"
            params.append(_utc_iso(from_))
        if to:
            sql += " AND COALESCE(published_at, fetched_at) <= ?"
            params.append(_utc_iso(to))
        count_sql = sql
        count_params = list(params)
        sql += " ORDER BY fetched_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(sql, params).fetchall()
        total = conn.execute(count_sql.replace("SELECT *", "SELECT COUNT(*)"), count_params).fetchone()[0]
        return {"count": total, "articles": [dict(r) for r in rows]}


def _utc_iso(value: datetime) -> str:
    normalized = value if value.tzinfo else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).replace(tzinfo=None).isoformat()
