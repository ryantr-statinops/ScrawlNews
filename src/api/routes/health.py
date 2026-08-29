from fastapi import APIRouter

from src.config import settings
from src.repositories.article_repo import ArticleRepository

router = APIRouter()


@router.get("/health")
def health():
    try:
        ArticleRepository(settings.database_url)
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"
    redis_status = "ok"
    try:
        import redis

        r = redis.from_url(settings.redis_url, socket_connect_timeout=1)
        r.ping()
    except Exception:
        redis_status = "unavailable (Stage 1-2 stub)"
    return {"status": "ok", "db": db_status, "redis": redis_status}
