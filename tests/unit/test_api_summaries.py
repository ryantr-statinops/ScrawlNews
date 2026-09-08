from fastapi.testclient import TestClient

from src.api.main import app
from src.config import settings
from src.models.summary import Summary
from src.repositories.summary_repo import SummaryRepository

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
    SummaryRepository(settings.database_url).save(
        Summary(id="sum-1", article_id="a-1", summary_text="A summary", model_used="fallback")
    )
    response = client.get("/api/summaries/sum-1")
    assert response.status_code == 200
    assert response.json()["summary_text"] == "A summary"


def test_get_summary_not_found():
    response = client.get("/api/summaries/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"error": "Resource not found"}
