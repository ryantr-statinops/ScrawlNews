from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config_validation import (
    validate_redis_url,
    validate_schedule_times,
    validate_sqlite_url,
    validate_timezone,
)


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite:///data/scrawlnews.db"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_enabled: bool = True
    llm_api_key: str = ""
    openrouter_api_key: str | None = None
    llm_provider: str = "openrouter"
    llm_model: str = "google/gemma-2-9b-it"
    fetch_limit: int = 20
    summary_lang: str = "vi"
    retention_days: int = 7
    news_categories: str = "technology,business,world,science"
    schedule_interval_hours: int = 24
    schedule_times: str = "08:00,12:00,18:00"
    schedule_timezone: str = "Asia/Ho_Chi_Minh"
    news_country: str = "VN"
    news_city: str = "Hanoi"
    dagster_shadow_db_url: str = "sqlite:///data/dagster-shadow/shadow.db"
    dagster_shadow_limit: int = 20
    dagster_shadow_categories: str = "technology"

    @field_validator("fetch_limit", "dagster_shadow_limit")
    @classmethod
    def check_limits(cls, value: int) -> int:
        if not 1 <= value <= 100:
            raise ValueError("must be between 1 and 100")
        return value

    @field_validator("retention_days")
    @classmethod
    def check_retention(cls, value: int) -> int:
        if not 1 <= value <= 30:
            raise ValueError("must be between 1 and 30")
        return value

    @field_validator("schedule_interval_hours")
    @classmethod
    def check_interval(cls, value: int) -> int:
        if not 1 <= value <= 168:
            raise ValueError("must be between 1 and 168")
        return value

    @field_validator("redis_url", "celery_broker_url", "celery_result_backend")
    @classmethod
    def check_redis_urls(cls, value: str) -> str:
        return validate_redis_url(value)

    @field_validator("database_url", "dagster_shadow_db_url")
    @classmethod
    def check_sqlite_urls(cls, value: str) -> str:
        return validate_sqlite_url(value)

    @field_validator("schedule_times")
    @classmethod
    def check_schedule_times(cls, value: str) -> str:
        return validate_schedule_times(value)

    @field_validator("schedule_timezone")
    @classmethod
    def check_schedule_timezone(cls, value: str) -> str:
        return validate_timezone(value)

    @property
    def news_categories_list(self) -> list[str]:
        return [c.strip().lower() for c in self.news_categories.split(",") if c.strip()]

    @property
    def dagster_shadow_categories_list(self) -> list[str]:
        return [c.strip().lower() for c in self.dagster_shadow_categories.split(",") if c.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def check_telegram(self):
        if self.telegram_enabled and self.app_env.lower() in {"production", "prod"}:
            if not self.telegram_bot_token or not self.telegram_chat_id:
                raise ValueError("Telegram credentials are required in production")
        return self


settings = Settings()
