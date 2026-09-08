import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from openai import APIStatusError
from telegram.error import BadRequest, Forbidden, NetworkError, RetryAfter
from urllib3.exceptions import HTTPError

from src.services.messenger import MessengerService
from src.services.scrawler import ScrawlerService
from src.services.synthesizer import SynthesizerService
from src.utils.errors import MessengerError, ScrawlerError, SynthesizerError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,retryable", [(400, False), (401, False), (408, True), (429, True), (503, True)]
)
async def test_rss_http_errors(status, retryable, mock_http_client):
    response = httpx.Response(status, request=httpx.Request("GET", "https://example.test"))
    mock_http_client.get.return_value = response
    with pytest.raises(ScrawlerError) as caught:
        await ScrawlerService().fetch_rss()
    assert caught.value.retryable is retryable
    assert isinstance(caught.value.__cause__, httpx.HTTPStatusError)


@pytest.mark.asyncio
async def test_rss_timeout(mock_http_client):
    error = httpx.ReadTimeout("timeout")
    mock_http_client.get.side_effect = error
    with pytest.raises(ScrawlerError) as caught:
        await ScrawlerService().fetch_rss()
    assert caught.value.retryable is True
    assert caught.value.__cause__ is error


@pytest.mark.asyncio
async def test_rss_invalid_protocol_is_not_retryable(mock_http_client):
    mock_http_client.get.side_effect = httpx.UnsupportedProtocol("invalid protocol")
    with pytest.raises(ScrawlerError) as caught:
        await ScrawlerService().fetch_rss()
    assert caught.value.retryable is False


@pytest.mark.asyncio
async def test_invalid_rss(mock_http_client):
    mock_http_client.get.return_value = httpx.Response(
        200, text="<broken", request=httpx.Request("GET", "https://example.test")
    )
    with pytest.raises(ScrawlerError, match="Invalid RSS") as caught:
        await ScrawlerService().fetch_rss()
    assert caught.value.retryable is False


@pytest.mark.asyncio
async def test_category_partial_fallback(sample_articles):
    service = ScrawlerService()
    with patch.object(service, "fetch_rss", side_effect=[ScrawlerError(), sample_articles]):
        assert await service.fetch_categories(["a", "b"]) == sample_articles


@pytest.mark.asyncio
async def test_category_empty_success_is_not_failure():
    service = ScrawlerService()
    with patch.object(service, "fetch_rss", side_effect=[ScrawlerError(), []]):
        assert await service.fetch_categories(["a", "b"]) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("retryable", [True, False])
async def test_all_categories_fail(retryable):
    service = ScrawlerService()
    error = ScrawlerError(retryable=retryable)
    with patch.object(service, "fetch_rss", side_effect=[ScrawlerError(), error]):
        with pytest.raises(ScrawlerError, match="All news categories failed") as caught:
            await service.fetch_categories(["a", "b"])
    assert caught.value.retryable is retryable
    assert caught.value.__cause__ is error


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [RuntimeError("bug"), sqlite3.OperationalError("database")])
async def test_category_does_not_swallow_unexpected_errors(error):
    service = ScrawlerService()
    with patch.object(service, "fetch_rss", side_effect=error):
        with pytest.raises(type(error)) as caught:
            await service.fetch_categories(["a", "b"])
    assert caught.value is error


@pytest.mark.asyncio
async def test_extraction_network_fallback():
    with patch("trafilatura.fetch_url", side_effect=HTTPError("offline")):
        assert await ScrawlerService().extract_content("https://example.test") is None


@pytest.mark.asyncio
async def test_extraction_bug_propagates():
    with patch("trafilatura.fetch_url", side_effect=TypeError("bug")):
        with pytest.raises(TypeError, match="bug"):
            await ScrawlerService().extract_content("https://example.test")


@pytest.mark.asyncio
@pytest.mark.parametrize("status,retryable", [(401, False), (429, True), (500, True)])
async def test_llm_error_classification_and_fallback(status, retryable, sample_articles):
    service = SynthesizerService()
    error = APIStatusError(
        "provider detail",
        body=None,
        response=httpx.Response(status, request=httpx.Request("POST", "https://example.test")),
    )
    service.client = MagicMock()
    service.client.chat.completions.create = AsyncMock(side_effect=error)
    with pytest.raises(SynthesizerError) as caught:
        await service.call_llm("prompt")
    assert caught.value.retryable is retryable
    assert caught.value.__cause__ is error
    result = await service.execute(sample_articles)
    assert [(s.summary_text, s.model_used) for s in result] == [
        (a.title, "fallback") for a in sample_articles
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["build_prompt", "call_llm", "parse_response"])
async def test_synthesizer_bugs_propagate(method, sample_articles):
    service = SynthesizerService()
    service.client = MagicMock()
    with patch.object(service, "call_llm", return_value="summary"):
        with patch.object(service, method, side_effect=TypeError("bug")):
            with pytest.raises(TypeError, match="bug"):
                await service.execute(sample_articles)


@pytest.mark.asyncio
@pytest.mark.parametrize("choices", [[], [MagicMock(message=MagicMock(content=None))]])
async def test_empty_llm_response_falls_back(choices, sample_articles):
    service = SynthesizerService()
    service.client = MagicMock()
    service.client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=choices))
    result = await service.execute(sample_articles)
    assert [(s.summary_text, s.model_used) for s in result] == [
        (a.title, "fallback") for a in sample_articles
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error,retryable",
    [
        (NetworkError("offline"), True),
        (RetryAfter(0), True),
        (BadRequest("invalid"), False),
        (Forbidden("denied"), False),
    ],
)
async def test_telegram_error_classification(error, retryable, mock_telegram_bot):
    mock_telegram_bot.send_message.side_effect = error
    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(MessengerError) as caught:
            await MessengerService().send_messages("123", ["message"])
    assert caught.value.retryable is retryable
    assert caught.value.__cause__ is error
    assert mock_telegram_bot.send_message.await_count == (2 if isinstance(error, RetryAfter) else 1)


@pytest.mark.asyncio
async def test_telegram_bug_propagates(mock_telegram_bot):
    mock_telegram_bot.send_message.side_effect = TypeError("bug")
    with pytest.raises(TypeError, match="bug"):
        await MessengerService().send_messages("123", ["message"])
