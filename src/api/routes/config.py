import logging

import redis
from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.config import settings
from src.config_validation import validate_schedule_times, validate_timezone
from src.repositories.config_repo import ConfigRepository
from src.utils.errors import ConfigError

logger = logging.getLogger(__name__)
router = APIRouter()

_config_repo = ConfigRepository(settings.database_url)
_SENSITIVE_CONFIG_KEYS = {
    "llm_api_key",
    "openrouter_api_key",
    "telegram_bot_token",
    "telegram_chat_id",
}


class SafeConfigResponse(BaseModel):
    fetch_limit: int
    summary_lang: str
    llm_provider: str
    llm_model: str
    llm_configured: bool
    telegram_enabled: bool
    telegram_configured: bool
    retention_days: int
    news_categories: str
    schedule_times: str
    schedule_timezone: str
    news_country: str
    news_city: str
    log_level: str


def _publish_config_change(changed_keys: list[str]) -> None:
    try:
        r = redis.from_url(settings.redis_url, socket_connect_timeout=1)
        r.publish("scrawlnews:config", ",".join(changed_keys))
    except redis.RedisError:
        logger.warning("Config saved but change notification unavailable", exc_info=True)


@router.get("/api/config", response_model=SafeConfigResponse)
def get_config() -> SafeConfigResponse:
    db_overrides = _config_repo.get_all()
    return SafeConfigResponse(
        fetch_limit=int(db_overrides.get("fetch_limit", settings.fetch_limit)),
        summary_lang=db_overrides.get("summary_lang", settings.summary_lang),
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        llm_configured=bool(settings.openrouter_api_key or settings.llm_api_key),
        telegram_enabled=db_overrides.get(
            "telegram_enabled", str(settings.telegram_enabled)
        ).lower()
        == "true",
        telegram_configured=bool(settings.telegram_bot_token and settings.telegram_chat_id),
        retention_days=int(db_overrides.get("retention_days", settings.retention_days)),
        news_categories=db_overrides.get("news_categories", settings.news_categories),
        schedule_times=db_overrides.get("schedule_times", settings.schedule_times),
        schedule_timezone=db_overrides.get("schedule_timezone", settings.schedule_timezone),
        news_country=db_overrides.get("news_country", settings.news_country),
        news_city=db_overrides.get("news_city", settings.news_city),
        log_level=settings.log_level,
    )


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
        "news_country",
        "news_city",
    }
    rejected = {k: v for k, v in payload.items() if k not in allowed}
    if rejected:
        raise ConfigError("Requested keys require restart")

    validated = dict(payload)
    # Validate every field before changing persistence, history, or live settings.
    for key, value in payload.items():
        if key in {"fetch_limit", "retention_days"}:
            try:
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError("Expected an integer")
                upper = 100 if key == "fetch_limit" else 30
                if not 1 <= value <= upper:
                    raise ValueError("Integer out of range")
            except ValueError as exc:
                raise ConfigError() from exc
        elif key == "telegram_enabled":
            if str(value).lower() not in {"true", "false"}:
                raise ConfigError()
        elif key == "schedule_times":
            try:
                validated[key] = validate_schedule_times(value)
            except (TypeError, ValueError) as exc:
                raise ConfigError() from exc
        elif key == "schedule_timezone":
            try:
                validate_timezone(value)
            except (TypeError, ValueError) as exc:
                raise ConfigError() from exc
        elif not isinstance(value, str):
            raise ConfigError()

    enabled = payload.get("telegram_enabled", settings.telegram_enabled)
    enabled = enabled is True or str(enabled).lower() == "true"
    if (
        enabled
        and settings.app_env.lower() in {"production", "prod"}
        and not (settings.telegram_bot_token and settings.telegram_chat_id)
    ):
        raise ConfigError()

    updated: dict[str, str] = {}
    changed_keys: list[str] = []
    for k, v in validated.items():
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
            elif k == "news_country":
                settings.news_country = str(v).upper()
            elif k == "news_city":
                settings.news_city = str(v)

    if changed_keys:
        _publish_config_change(changed_keys)

    return {"updated": updated}


@router.get("/api/config/history")
def get_config_history(key: str | None = Query(None), limit: int = Query(50, le=200)):
    history = _config_repo.get_history(key=key, limit=limit)
    return {"history": [item for item in history if item.get("key") not in _SENSITIVE_CONFIG_KEYS]}
