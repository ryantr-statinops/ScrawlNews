from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_list_summaries():
    response = client.get("/api/summaries")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "summaries" in data


def test_list_summaries_with_article_filter():
    response = client.get("/api/summaries?article_id=abc123")
    assert response.status_code == 200


def test_get_summary_detail():
    response = client.get("/api/summaries/sum-1")
    assert response.status_code in (200, 404)


def test_get_summary_not_found():
    response = client.get("/api/summaries/nonexistent")
    assert response.status_code == 200
    assert "error" in response.json()
