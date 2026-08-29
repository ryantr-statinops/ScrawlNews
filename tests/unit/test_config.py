import pytest
from src.config import Settings
from src.repositories.config_repo import ConfigRepository


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


class TestConfigRepository:
    def test_set_and_get(self, temp_db):
        repo = ConfigRepository(f"sqlite:///{temp_db}")
        repo.set("fetch_limit", "50")
        assert repo.get("fetch_limit") == "50"

    def test_set_many(self, temp_db):
        repo = ConfigRepository(f"sqlite:///{temp_db}")
        repo.set_many({"fetch_limit": "30", "summary_lang": "en"})
        assert repo.get("fetch_limit") == "30"
        assert repo.get("summary_lang") == "en"

    def test_get_all_empty(self, temp_db):
        repo = ConfigRepository(f"sqlite:///{temp_db}")
        assert repo.get_all() == {}

    def test_log_change(self, temp_db):
        repo = ConfigRepository(f"sqlite:///{temp_db}")
        repo.set("fetch_limit", "20")
        repo.log_change("fetch_limit", "10", "20")
        history = repo.get_history(key="fetch_limit")
        assert len(history) == 1
        assert history[0]["old_value"] == "10"
        assert history[0]["new_value"] == "20"

    def test_get_history_empty(self, temp_db):
        repo = ConfigRepository(f"sqlite:///{temp_db}")
        assert repo.get_history() == []
