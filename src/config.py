from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def check_telegram(self):
        if self.telegram_enabled and not self.telegram_bot_token:
            # allow missing in local dev, but warn via validator - don't raise in dev
            # raise only if explicitly required
            pass
        return self


settings = Settings()
