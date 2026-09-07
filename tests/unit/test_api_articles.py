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


def test_list_articles_with_category_filter(temp_db):
    from unittest.mock import patch

    from src.models.article import Article
    from src.repositories.article_repo import ArticleRepository

    repo = ArticleRepository(f"sqlite:///{temp_db}")
    repo.save(Article(id="c1", url="https://c1.com", title="T1", category="tech"))
    repo.save(Article(id="c2", url="https://c2.com", title="T2", category="sports"))
    with patch("src.api.routes.articles.settings.database_url", f"sqlite:///{temp_db}"):
        response = client.get("/api/articles?category=tech")
    assert response.status_code == 200
    articles = response.json()["articles"]
    assert len(articles) == 1
    assert articles[0]["id"] == "c1"


def test_list_articles_pagination():
    response = client.get("/api/articles?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) <= 10
