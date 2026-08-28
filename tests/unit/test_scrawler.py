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


@pytest.mark.asyncio
async def test_fetch_rss_empty():
    service = ScrawlerService()
    xml = """<rss><channel><item><title>T</title><link>http://a.com</link></item></channel></rss>"""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        client.get.return_value.text = xml
        client.get.return_value.raise_for_status = lambda: None
        articles = await service.fetch_rss(limit=0)
        assert articles == []


@pytest.mark.asyncio
async def test_fetch_rss_network_error():
    service = ScrawlerService()
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        client.get.side_effect = Exception("Network error")
        with pytest.raises(Exception):
            await service.fetch_rss(limit=5)


@pytest.mark.asyncio
async def test_extract_content_success():
    service = ScrawlerService()
    html = "<html><body><article>Content here</article></body></html>"
    with patch("trafilatura.fetch_url", return_value=html):
        with patch("trafilatura.extract", return_value="Extracted content"):
            result = await service.extract_content("https://example.com")
            assert result == "Extracted content"


@pytest.mark.asyncio
async def test_extract_content_failure():
    service = ScrawlerService()
    with patch("trafilatura.fetch_url", return_value=None):
        result = await service.extract_content("https://example.com")
        assert result is None


@pytest.mark.asyncio
async def test_extract_content_trafilatura_returns_none():
    service = ScrawlerService()
    html = "<html><body></body></html>"
    with patch("trafilatura.fetch_url", return_value=html):
        with patch("trafilatura.extract", return_value=None):
            result = await service.extract_content("https://example.com")
            assert result is None


@pytest.mark.asyncio
async def test_fetch_playwright_fallback_stub():
    service = ScrawlerService()
    articles = await service.fetch_playwright_fallback(limit=5)
    assert articles == []


@pytest.mark.asyncio
async def test_execute_calls_fetch_rss():
    service = ScrawlerService()
    with patch.object(service, "fetch_rss", return_value=[]) as mock_fetch:
        result = await service.execute(limit=10)
        mock_fetch.assert_called_once_with(limit=10)
        assert result == []
