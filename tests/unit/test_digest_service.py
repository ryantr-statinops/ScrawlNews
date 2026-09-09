import pytest

from src.models.summary import Summary
from src.services.digest_service import DigestService


@pytest.mark.asyncio
async def test_digest_service_falls_back_without_llm(sample_articles, monkeypatch):
    monkeypatch.setattr("src.config.settings.openrouter_api_key", None)
    articles = sample_articles[:1]
    summaries = [Summary("s1", articles[0].id, "A useful summary", "test")]
    digest = await DigestService().execute("technology", articles, summaries)
    assert digest.status == "ready"
    assert digest.model_used == "fallback"
    assert articles[0].title in digest.digest_text
