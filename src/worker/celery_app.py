from celery import Celery
from src.config import settings

celery_app = Celery(
    "scrawlnews",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Stage 1 stub: no tasks yet, real pipeline_run in Stage 2
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
