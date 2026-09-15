from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "fetch_limit" in data
    assert "summary_lang" in data
    assert "telegram_enabled" in data
    assert data["llm_configured"] is False
    assert data["telegram_configured"] is False


def test_get_config_never_returns_secret_values(monkeypatch):
    monkeypatch.setattr("src.api.routes.config.settings.llm_api_key", "llm-secret")
    monkeypatch.setattr("src.api.routes.config.settings.telegram_bot_token", "bot-secret")
    monkeypatch.setattr("src.api.routes.config.settings.telegram_chat_id", "chat-secret")

    response = client.get("/api/config")

    assert response.status_code == 200
    data = response.json()
    assert data["llm_configured"] is True
    assert data["telegram_configured"] is True
    assert "llm-secret" not in response.text
    assert "bot-secret" not in response.text
    assert "chat-secret" not in response.text


def test_update_config_allowed_keys():
    response = client.put("/api/config", json={"fetch_limit": 50})
    assert response.status_code == 200
    data = response.json()
    assert "updated" in data


def test_update_config_multiple_keys():
    response = client.put(
        "/api/config", json={"fetch_limit": 50, "summary_lang": "en", "telegram_enabled": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["updated"]) == 3


def test_update_config_disallowed_key():
    response = client.put("/api/config", json={"llm_api_key": "secret"})
    assert response.status_code == 400
    data = response.json()
    assert data == {"error": "Invalid configuration"}
