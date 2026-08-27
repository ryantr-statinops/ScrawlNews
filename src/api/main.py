from fastapi import FastAPI
from src.config import settings
from src.repositories.article_repo import ArticleRepository
from src.repositories.summary_repo import SummaryRepository
from src.repositories.run_repo import PipelineRunRepository

app = FastAPI(title="ScrawlNews Dashboard", version="0.2.0")


@app.get("/health")
def health():
    # simple check, repos init will create DB if missing
    try:
        ArticleRepository(settings.database_url)
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"
    # redis check is optional for Stage 1 stub
    redis_status = "ok"
    try:
        import redis

        r = redis.from_url(settings.redis_url, socket_connect_timeout=1)
        r.ping()
    except Exception:
        redis_status = "unavailable (Stage 1 stub)"
    return {"status": "ok", "db": db_status, "redis": redis_status}


@app.get("/api/articles")
def list_articles(limit: int = 20, offset: int = 0):
    return {"count": 0, "articles": []}


@app.get("/api/summaries")
def list_summaries(limit: int = 20):
    return {"count": 0, "summaries": []}


@app.get("/api/runs")
def list_runs(limit: int = 20):
    return {"runs": []}


@app.post("/api/runs")
def trigger_run(fetch_limit: int | None = None, dry_run: bool = False):
    # Stage 1 stub: return fake task id, real Celery in Stage 2
    return {"task_id": "stub-task-id", "status": "pending", "run_id": "stub-run-id"}


@app.get("/api/config")
def get_config():
    return {
        "fetch_limit": settings.fetch_limit,
        "summary_lang": settings.summary_lang,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "telegram_enabled": settings.telegram_enabled,
        "retention_days": settings.retention_days,
        "log_level": settings.log_level,
    }


@app.put("/api/config")
def update_config(payload: dict):
    # Stage 1 stub: only allow 4 hot-reload vars
    allowed = {"fetch_limit", "summary_lang", "telegram_enabled", "retention_days"}
    for k in payload:
        if k not in allowed:
            return {"error": f"key {k} requires restart"}
    # in real Stage 2 would update in-memory settings
    return {"updated": {k: payload[k] for k in payload if k in allowed}}
