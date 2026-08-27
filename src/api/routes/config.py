from fastapi import APIRouter
from src.config import settings

router = APIRouter()


@router.get("/api/config")
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


@router.put("/api/config")
def update_config(payload: dict):
    allowed = {"fetch_limit", "summary_lang", "telegram_enabled", "retention_days"}
    for k in payload:
        if k not in allowed:
            return {"error": f"key {k} requires restart"}
    return {"updated": {k: payload[k] for k in payload if k in allowed}}
