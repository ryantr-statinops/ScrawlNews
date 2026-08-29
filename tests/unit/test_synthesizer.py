from unittest.mock import AsyncMock

import pytest

from src.models.summary import Summary
from src.services.synthesizer import SynthesizerService


@pytest.mark.asyncio
async def test_summarize_empty_list():
    service = SynthesizerService()
    result = await service.execute([])
    assert result == []


@pytest.mark.asyncio
async def test_summarize_batch(mock_openai, sample_articles):
    mock_openai.chat.completions.create.return_value = AsyncMock(
        choices=[AsyncMock(message=AsyncMock(content="Summary text"))]
    )
    service = SynthesizerService()
    service.client = mock_openai
    result = await service.execute(sample_articles)
    assert len(result) == len(sample_articles)
    assert all(isinstance(s, Summary) for s in result)


@pytest.mark.asyncio
async def test_llm_error_fallback(mock_openai, sample_articles):
    mock_openai.chat.completions.create.side_effect = Exception("API error")
    service = SynthesizerService()
    service.client = mock_openai
    result = await service.execute(sample_articles)
    assert len(result) == len(sample_articles)
    assert all(s.model_used == "fallback" for s in result)


@pytest.mark.asyncio
async def test_build_prompt(sample_articles):
    service = SynthesizerService()
    prompt = service.build_prompt(sample_articles)
    assert "news summarizer" in prompt
    assert sample_articles[0].title in prompt


@pytest.mark.asyncio
async def test_call_llm(mock_openai):
    mock_openai.chat.completions.create.return_value = AsyncMock(
        choices=[AsyncMock(message=AsyncMock(content="Test response"))]
    )
    service = SynthesizerService()
    service.client = mock_openai
    result = await service.call_llm("test prompt")
    assert result == "Test response"


@pytest.mark.asyncio
async def test_no_client_fallback(sample_articles):
    service = SynthesizerService()
    service.client = None
    result = await service.execute(sample_articles)
    assert len(result) == len(sample_articles)
    assert all(s.summary_text == a.title for s, a in zip(result, sample_articles))
