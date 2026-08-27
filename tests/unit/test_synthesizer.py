import pytest
from src.services.synthesizer import SynthesizerService
from src.models.article import Article
from datetime import datetime


@pytest.mark.asyncio
async def test_synthesizer_fallback():
    service = SynthesizerService()
    service.client = None
    articles = [Article(id="a", url="http://a.com", title="Hello")]
    summaries = await service.execute(articles)
    assert len(summaries) == 1
    assert summaries[0].summary_text == "Hello"
