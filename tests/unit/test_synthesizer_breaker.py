from unittest.mock import AsyncMock, patch

import pytest
from openai import APIConnectionError, APIStatusError

from src.services.synthesizer import SynthesizerService, _llm_breaker
from src.utils.errors import SynthesizerError


@pytest.fixture(autouse=True)
def reset_llm_breaker():
    _llm_breaker.reset()
    yield
    _llm_breaker.reset()


@pytest.mark.asyncio
async def test_llm_breaker_opens_after_repeated_failures():
    svc = SynthesizerService()
    svc.client = AsyncMock()
    svc.client.chat.completions.create.side_effect = APIConnectionError(
        request=AsyncMock()
    )
    from src.models.article import Article

    articles = [Article(id="a1", url="https://x.com", title="T")]
    for _ in range(5):
        with pytest.raises(SynthesizerError, match="LLM transport failed"):
            await svc.call_llm("prompt")
    assert _llm_breaker.state.value == "open"
    with pytest.raises(SynthesizerError, match="circuit breaker is open"):
        await svc.call_llm("prompt")


@pytest.mark.asyncio
async def test_llm_breaker_blocks_when_open():
    _llm_breaker.record_failure()
    _llm_breaker.record_failure()
    _llm_breaker.record_failure()
    _llm_breaker.record_failure()
    _llm_breaker.record_failure()
    svc = SynthesizerService()
    svc.client = AsyncMock()
    with pytest.raises(SynthesizerError, match="circuit breaker is open"):
        await svc.call_llm("prompt")


@pytest.mark.asyncio
async def test_llm_breaker_closes_on_success():
    svc = SynthesizerService()
    svc.client = AsyncMock()
    mock_resp = AsyncMock()
    mock_resp.choices = [AsyncMock(message=AsyncMock(content="summary text"))]
    svc.client.chat.completions.create.return_value = mock_resp
    for _ in range(3):
        _llm_breaker.record_failure()
    assert _llm_breaker.state.value == "closed"
    result = await svc.call_llm("prompt")
    assert result == "summary text"
    assert _llm_breaker._failure_count == 0


@pytest.mark.asyncio
async def test_execute_falls_back_when_breaker_open():
    from src.models.article import Article

    _llm_breaker.record_failure()
    _llm_breaker.record_failure()
    _llm_breaker.record_failure()
    _llm_breaker.record_failure()
    _llm_breaker.record_failure()
    svc = SynthesizerService()
    svc.client = AsyncMock()
    articles = [Article(id="a1", url="https://x.com", title="My Title")]
    result = await svc.execute(articles)
    assert result[0].summary_text == "My Title"
    assert result[0].model_used == "fallback"
