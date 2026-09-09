import logging

import redis
from fastapi import APIRouter, Query

from src.config import settings
from src.repositories.config_repo import ConfigRepository
from src.utils.errors import ConfigError

logger = logging.getLogger(__name__)
router = APIRouter()

_config_repo = ConfigRepository(settings.database_url)


def _publish_config_change(changed_keys: list[str]) -> None:
    try:
        r = redis.from_url(settings.redis_url, socket_connect_timeout=1)
        r.publish("scrawlnews:config", ",".join(changed_keys))
    except redis.RedisError:
        logger.warning("Config saved but change notification unavailable", exc_info=True)


@router.get("/api/config")
def get_config():
    db_overrides = _config_repo.get_all()
    return {
        "fetch_limit": int(db_overrides.get("fetch_limit", settings.fetch_limit)),
        "summary_lang": db_overrides.get("summary_lang", settings.summary_lang),
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "telegram_enabled": db_overrides.get(
            "telegram_enabled", str(settings.telegram_enabled)
        ).lower()
        == "true",
        "retention_days": int(db_overrides.get("retention_days", settings.retention_days)),
        "news_categories": db_overrides.get("news_categories", settings.news_categories),
        "schedule_times": db_overrides.get("schedule_times", settings.schedule_times),
        "schedule_timezone": db_overrides.get("schedule_timezone", settings.schedule_timezone),
        "log_level": settings.log_level,
    }


@router.put("/api/config")
def update_config(payload: dict):
    allowed = {
        "fetch_limit",
        "summary_lang",
        "telegram_enabled",
        "retention_days",
        "news_categories",
        "schedule_times",
        "schedule_timezone",
    }
    rejected = {k: v for k, v in payload.items() if k not in allowed}
    if rejected:
        raise ConfigError("Requested keys require restart")

    # Validate the whole request before changing persisted or in-memory settings.
    for key, value in payload.items():
        if key in {"fetch_limit", "retention_days"}:
            try:
                if isinstance(value, bool) or not isinstance(value, (str, int)):
                    raise ValueError("Expected an integer")
                if int(value) < (1 if key == "fetch_limit" else 0):
                    raise ValueError("Integer out of range")
            except ValueError as exc:
                raise ConfigError("Invalid numeric configuration") from exc
        elif key == "telegram_enabled":
            if str(value).lower() not in {"true", "false"}:
                raise ConfigError("Invalid Telegram toggle")
        elif key == "schedule_times":
            if not isinstance(value, str) or not all(_valid_time(item) for item in value.split(",") if item.strip()):
                raise ConfigError("Invalid schedule times")
        elif not isinstance(value, str):
            raise ConfigError("Expected a configuration string")

    updated: dict[str, str] = {}
    changed_keys: list[str] = []
    for k, v in payload.items():
        if k in allowed:
            old_value = _config_repo.get(k)
            new_value = str(v)
            _config_repo.set(k, new_value)
            _config_repo.log_change(k, old_value, new_value)
            updated[k] = new_value
            changed_keys.append(k)
            if k == "fetch_limit":
                settings.fetch_limit = int(v)
            elif k == "summary_lang":
                settings.summary_lang = str(v)
            elif k == "telegram_enabled":
                settings.telegram_enabled = str(v).lower() == "true"
            elif k == "retention_days":
                settings.retention_days = int(v)
            elif k == "news_categories":
                settings.news_categories = str(v)
            elif k == "schedule_times":
                settings.schedule_times = str(v)
            elif k == "schedule_timezone":
                settings.schedule_timezone = str(v)

    if changed_keys:
        _publish_config_change(changed_keys)

    return {"updated": updated}


@router.get("/api/config/history")
def get_config_history(key: str | None = Query(None), limit: int = Query(50, le=200)):
    return {"history": _config_repo.get_history(key=key, limit=limit)}


def _valid_time(value: str) -> bool:
    try:
        hour, minute = (int(part) for part in value.strip().split(":"))
        return 0 <= hour <= 23 and 0 <= minute <= 59
    except (TypeError, ValueError):
        return False
