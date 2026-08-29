from fastapi import APIRouter, Query
from src.config import settings
from src.repositories.config_repo import ConfigRepository

router = APIRouter()

_config_repo = ConfigRepository(settings.database_url)


@router.get("/api/config")
def get_config():
    db_overrides = _config_repo.get_all()
    return {
        "fetch_limit": int(db_overrides.get("fetch_limit", settings.fetch_limit)),
        "summary_lang": db_overrides.get("summary_lang", settings.summary_lang),
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "telegram_enabled": db_overrides.get("telegram_enabled", str(settings.telegram_enabled)).lower() == "true",
        "retention_days": int(db_overrides.get("retention_days", settings.retention_days)),
        "log_level": settings.log_level,
    }


@router.put("/api/config")
def update_config(payload: dict):
    allowed = {"fetch_limit", "summary_lang", "telegram_enabled", "retention_days"}
    rejected = {k: v for k, v in payload.items() if k not in allowed}
    if rejected:
        return {"error": f"keys require restart: {', '.join(rejected.keys())}"}

    updated: dict[str, str] = {}
    for k, v in payload.items():
        if k in allowed:
            old_value = _config_repo.get(k)
            new_value = str(v)
            _config_repo.set(k, new_value)
            _config_repo.log_change(k, old_value, new_value)
            updated[k] = new_value
            if k == "fetch_limit":
                settings.fetch_limit = int(v)
            elif k == "summary_lang":
                settings.summary_lang = str(v)
            elif k == "telegram_enabled":
                settings.telegram_enabled = str(v).lower() == "true"
            elif k == "retention_days":
                settings.retention_days = int(v)

    return {"updated": updated}


@router.get("/api/config/history")
def get_config_history(key: str | None = Query(None), limit: int = Query(50, le=200)):
    return {"history": _config_repo.get_history(key=key, limit=limit)}
