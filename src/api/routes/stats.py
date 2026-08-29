import sqlite3

from fastapi import APIRouter

from src.config import settings
from src.repositories.article_repo import ArticleRepository

router = APIRouter()


@router.get("/api/stats")
def get_stats(days: int = 7):
    repo = ArticleRepository(settings.database_url)
    with sqlite3.connect(repo.db_path) as conn:
        conn.row_factory = sqlite3.Row
        articles_per_day = conn.execute(
            "SELECT date(fetched_at) as day, COUNT(*) as count FROM articles WHERE fetched_at >= date('now', ?) GROUP BY day ORDER BY day",
            (f"-{days} days",),
        ).fetchall()
        summaries_per_day = conn.execute(
            "SELECT date(created_at) as day, COUNT(*) as count FROM summaries WHERE created_at >= date('now', ?) GROUP BY day ORDER BY day",
            (f"-{days} days",),
        ).fetchall()
        source_dist = conn.execute(
            "SELECT source, COUNT(*) as count FROM articles GROUP BY source"
        ).fetchall()
        return {
            "articles_per_day": [dict(r) for r in articles_per_day],
            "summaries_per_day": [dict(r) for r in summaries_per_day],
            "source_dist": [dict(r) for r in source_dist],
            "cost_estimate": 0.0,
        }
