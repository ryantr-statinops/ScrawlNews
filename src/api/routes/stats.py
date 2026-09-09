import sqlite3

from fastapi import APIRouter, Query

from src.config import settings
from src.repositories.article_repo import ArticleRepository

router = APIRouter()


@router.get("/api/stats")
def get_stats(days: int = Query(7, ge=1, le=365)):
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
            "SELECT COALESCE(source, 'unknown') as source, COUNT(*) as count FROM articles WHERE fetched_at >= date('now', ?) GROUP BY source ORDER BY count DESC",
            (f"-{days} days",),
        ).fetchall()
        category_dist = conn.execute(
            "SELECT COALESCE(category, 'uncategorized') as category, COUNT(*) as count FROM articles WHERE fetched_at >= date('now', ?) GROUP BY category ORDER BY count DESC",
            (f"-{days} days",),
        ).fetchall()
        totals = conn.execute(
            """SELECT COUNT(*) AS articles, COALESCE(SUM(summarized), 0) AS summarized,
            (SELECT COUNT(*) FROM summaries WHERE created_at >= date('now', ?)) AS summaries
            FROM articles WHERE fetched_at >= date('now', ?)""",
            (f"-{days} days", f"-{days} days"),
        ).fetchone()
        return {
            "days": days,
            "totals": dict(totals) if totals else {"articles": 0, "summarized": 0, "summaries": 0},
            "articles_per_day": [dict(r) for r in articles_per_day],
            "summaries_per_day": [dict(r) for r in summaries_per_day],
            "source_dist": [dict(r) for r in source_dist],
            "category_dist": [dict(r) for r in category_dist],
            "cost_estimate": 0.0,
        }
