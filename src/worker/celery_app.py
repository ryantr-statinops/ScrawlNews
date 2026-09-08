from celery import Celery
from celery.signals import worker_process_init

from src.config import settings


def _setup_celery_logging(**_kwargs):
    from src.utils.logging import setup_logging

    setup_logging(settings.log_level)


worker_process_init.connect(_setup_celery_logging)

celery_app = Celery(
    "scrawlnews",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Ensure pipeline.run task is registered for worker (bottom import avoids circular import)
import src.worker.tasks  # noqa: E402, F401

celery_app.autodiscover_tasks(["src.worker.tasks"])
