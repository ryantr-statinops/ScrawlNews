from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_list_articles_empty():
    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "articles" in data


def test_list_articles_with_search():
    response = client.get("/api/articles?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data


def test_list_articles_with_source_filter():
    response = client.get("/api/articles?source=TechCrunch")
    assert response.status_code == 200


def test_list_articles_pagination():
    response = client.get("/api/articles?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) <= 10
