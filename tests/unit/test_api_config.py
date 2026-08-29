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
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
