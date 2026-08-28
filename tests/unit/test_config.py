from src.config import Settings


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.app_env == "local"
        assert settings.log_level == "INFO"
        assert settings.database_url == "sqlite:///data/scrawlnews.db"
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.celery_broker_url == "redis://localhost:6379/0"
        assert settings.celery_result_backend == "redis://localhost:6379/1"
        assert settings.telegram_enabled is True
        assert settings.llm_provider == "openrouter"
        assert settings.llm_model == "google/gemma-2-9b-it"
        assert settings.fetch_limit == 20
        assert settings.summary_lang == "vi"
        assert settings.retention_days == 7

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("FETCH_LIMIT", "50")
        monkeypatch.setenv("SUMMARY_LANG", "en")
        monkeypatch.setenv("TELEGRAM_ENABLED", "false")
        settings = Settings()
        assert settings.fetch_limit == 50
        assert settings.summary_lang == "en"
        assert settings.telegram_enabled is False

    def test_telegram_enabled_without_token(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_ENABLED", "true")
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
        settings = Settings()
        assert settings.telegram_enabled is True

    def test_telegram_disabled_with_token(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_ENABLED", "false")
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456")
        settings = Settings()
        assert settings.telegram_enabled is False

    def test_extra_fields_ignored(self, monkeypatch):
        monkeypatch.setenv("UNKNOWN_FIELD", "value")
        settings = Settings()
        assert not hasattr(settings, "unknown_field")
