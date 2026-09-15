import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.summary import Summary
from src.services.digest_service import DigestService
from src.services.messenger import MessengerService
from src.services.scrawler import ScrawlerService
from src.services.synthesizer import SynthesizerService


def _load_shadow_fixture() -> dict:
    path = Path(__file__).parents[1] / "fixtures" / "shadow_pipeline.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_shadow_fixture_rss_and_extraction(sample_rss_xml):
    fixture = _load_shadow_fixture()
    service = ScrawlerService()
    client = AsyncMock()
    client.get.return_value.text = sample_rss_xml
    client.get.return_value.raise_for_status = lambda: None

    with patch("httpx.AsyncClient") as http_client:
        http_client.return_value.__aenter__.return_value = client
        with patch.object(service, "extract_content", return_value=fixture["extraction_content"]):
            articles = asyncio.run(service.fetch_rss(2))

    assert len(articles) == 2
    assert articles[0].content == fixture["extraction_content"]
    assert articles[0].url == "https://example.com/article1"


@pytest.mark.asyncio
async def test_shadow_fixture_summary(sample_articles):
    fixture = _load_shadow_fixture()
    service = SynthesizerService()
    service.client = MagicMock()
    service.call_llm = AsyncMock(return_value=fixture["summary_response"])

    summaries = await service.execute(sample_articles[:2], run_id="fixture-run")

    assert [summary.article_id for summary in summaries] == [article.id for article in sample_articles[:2]]
    assert all(summary.summary_text == fixture["summary_response"] for summary in summaries)


@pytest.mark.asyncio
async def test_shadow_fixture_digest(sample_articles):
    fixture = _load_shadow_fixture()
    article = sample_articles[0]
    summary = Summary("summary-1", article.id, "Summary", "fixture-model")
    service = DigestService()
    service.synthesizer.client = MagicMock()
    service.synthesizer.call_llm = AsyncMock(return_value=fixture["digest_response"])

    digest = await service.execute("technology", [article], [summary], run_id="fixture-run")

    assert digest.status == "ready"
    assert digest.digest_text == fixture["digest_response"]
    assert digest.article_count == 1


@pytest.mark.asyncio
async def test_shadow_fixture_delivery_is_disabled(monkeypatch):
    fixture = _load_shadow_fixture()
    monkeypatch.setattr("src.config.settings.telegram_enabled", fixture["telegram_enabled"])
    service = MessengerService()

    with patch.object(service, "send_messages") as send_messages:
        delivered = await service.execute(
            [Summary("summary-1", "article-1", "Summary", "fixture-model")]
        )

    assert delivered is True
    send_messages.assert_not_called()
