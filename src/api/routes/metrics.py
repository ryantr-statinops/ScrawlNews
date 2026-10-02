import logging
import sqlite3

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest

from src.config import settings
from src.metrics import ScrawlNewsCollector

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/metrics", include_in_schema=False)
def metrics():
    registry = CollectorRegistry()
    try:
        ScrawlNewsCollector(settings.database_url).collect(registry)
    except (sqlite3.Error, OSError) as exc:
        logger.error("Prometheus metrics database collection failed", exc_info=exc)
        return Response(content="Metrics temporarily unavailable\n", status_code=503)
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
