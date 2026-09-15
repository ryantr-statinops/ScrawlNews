from src.config import settings
from src.dagster_project.shadow import isolated_settings, shadow_database_path


def test_shadow_database_path_uses_configured_namespace(monkeypatch, tmp_path):
    configured = tmp_path / "shadow" / "base.db"
    monkeypatch.setattr(settings, "dagster_shadow_db_url", f"sqlite:///{configured}")

    path = shadow_database_path("run-123")

    assert path == configured.parent / "run-123.db"
    assert path.parent.is_dir()


def test_isolated_settings_restores_production_values(monkeypatch, tmp_path):
    configured = tmp_path / "shadow" / "base.db"
    monkeypatch.setattr(settings, "dagster_shadow_db_url", f"sqlite:///{configured}")
    monkeypatch.setattr(settings, "database_url", "sqlite:///data/scrawlnews.db")
    monkeypatch.setattr(settings, "telegram_enabled", True)

    with isolated_settings("run-456") as shadow_path:
        assert shadow_path == configured.parent / "run-456.db"
        assert settings.database_url == f"sqlite:///{shadow_path}"
        assert settings.telegram_enabled is False

    assert settings.database_url == "sqlite:///data/scrawlnews.db"
    assert settings.telegram_enabled is True


def test_isolated_settings_restores_values_after_failure(monkeypatch, tmp_path):
    configured = tmp_path / "shadow" / "base.db"
    monkeypatch.setattr(settings, "dagster_shadow_db_url", f"sqlite:///{configured}")
    monkeypatch.setattr(settings, "database_url", "sqlite:///production.db")
    monkeypatch.setattr(settings, "telegram_enabled", False)

    try:
        with isolated_settings("run-failure"):
            raise RuntimeError("fixture failure")
    except RuntimeError:
        pass

    assert settings.database_url == "sqlite:///production.db"
    assert settings.telegram_enabled is False


def test_shadow_categories_are_normalized(monkeypatch):
    monkeypatch.setattr(settings, "dagster_shadow_categories", " Technology, business, ,WORLD ")

    assert settings.dagster_shadow_categories_list == ["technology", "business", "world"]
