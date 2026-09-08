import logging
import sqlite3

import redis
from fastapi import APIRouter

from src.config import settings
from src.repositories.article_repo import ArticleRepository
from src.services.messenger import _telegram_breaker
from src.services.synthesizer import _llm_breaker

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health():
    try:
        ArticleRepository(settings.database_url)
        db_status = "ok"
    except (sqlite3.Error, OSError):
        logger.warning("Health database check failed", exc_info=True)
        db_status = "unavailable"
    redis_status = "ok"
    try:
        r = redis.from_url(settings.redis_url, socket_connect_timeout=1)
        r.ping()
    except redis.RedisError:
        redis_status = "unavailable (Stage 1-2 stub)"
    return {
        "status": "ok",
        "db": db_status,
        "redis": redis_status,
        "circuit_breakers": {
            "llm": _llm_breaker.to_dict(),
            "telegram": _telegram_breaker.to_dict(),
        },
    }
