from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_list_sources_includes_default_catalog():
    response = client.get("/api/sources?q=technology")
    assert response.status_code == 200
    assert response.json()["sources"][0]["id"] == "google-vn-tech"


def test_create_source_rejects_non_http_url():
    response = client.post("/api/sources", json={"name": "Bad", "url": "file:///tmp/feed"})
    assert response.status_code == 422


def test_test_builtin_source():
    with patch("src.api.routes.sources.settings.database_url", "sqlite:///data/test-sources.db"):
        response = client.post("/api/sources/google-vn-tech/test")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
