from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check_integration():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_config_roundtrip():
    get_response = client.get("/api/config")
    assert get_response.status_code == 200
    config = get_response.json()

    update_response = client.put("/api/config", json={"fetch_limit": config.get("fetch_limit", 20)})
    assert update_response.status_code == 200


def test_articles_endpoint_integration():
    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "articles" in data


def test_summaries_endpoint_integration():
    response = client.get("/api/summaries")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "summaries" in data
