from src.worker.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, name="pipeline.run")
def pipeline_run(self, fetch_limit: int | None = None):
    # Stage 1 stub: real logic in Stage 2
    return {"status": "stub", "fetch_limit": fetch_limit}
