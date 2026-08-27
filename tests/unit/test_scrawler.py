import pytest
from unittest.mock import AsyncMock, patch
from src.services.scrawler import ScrawlerService


@pytest.mark.asyncio
async def test_fetch_rss_success():
    service = ScrawlerService()
    xml = """<rss><channel><item><title>T</title><link>http://a.com</link></item></channel></rss>"""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        client.get.return_value.text = xml
        client.get.return_value.raise_for_status = lambda: None
        with patch.object(service, "extract_content", return_value="content"):
            articles = await service.fetch_rss(limit=5)
            assert len(articles) == 1
            assert articles[0].url == "http://a.com"
