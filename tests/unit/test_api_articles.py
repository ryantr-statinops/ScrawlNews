from unittest.mock import patch

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
    assert response.json()["count"] == 1
    articles = response.json()["articles"]
    assert len(articles) == 1
    assert articles[0]["id"] == "c1"


def test_list_articles_pagination():
    response = client.get("/api/articles?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) <= 10


def test_list_articles_filters_publication_window(temp_db):
    from datetime import datetime

    from src.models.article import Article
    from src.repositories.article_repo import ArticleRepository

    repo = ArticleRepository(f"sqlite:///{temp_db}")
    repo.save(
        Article(
            id="old",
            url="https://old.example",
            title="Old",
            published_at=datetime(2025, 1, 1),
        )
    )
    repo.save(
        Article(
            id="new",
            url="https://new.example",
            title="New",
            published_at=datetime(2025, 2, 1),
        )
    )
    with patch("src.api.routes.articles.settings.database_url", f"sqlite:///{temp_db}"):
        response = client.get("/api/articles?from=2025-01-15T00:00:00Z&to=2025-02-15T00:00:00Z")
    assert response.status_code == 200
    assert [article["id"] for article in response.json()["articles"]] == ["new"]
