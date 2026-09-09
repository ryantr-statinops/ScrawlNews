import asyncio
import calendar
import hashlib
import logging
from datetime import UTC, datetime
from time import perf_counter

import feedparser
import httpx
import trafilatura
from urllib3.exceptions import HTTPError

from src.config import settings
from src.models.article import Article
from src.services.base import BaseService
from src.utils.errors import ScrawlerError

logger = logging.getLogger(__name__)


def _entry_datetime(entry) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    try:
        return datetime.fromtimestamp(calendar.timegm(parsed), tz=UTC)
    except (TypeError, ValueError):
        return None


class ScrawlerService(BaseService):
    async def execute(self, limit: int = 20, categories: list[str] | None = None) -> list[Article]:
        self.fetch_events: list[dict] = []
        configured_sources = self._configured_sources()
        if configured_sources:
            return await self.fetch_sources(configured_sources, limit)
        cats = categories or self._configured_categories()
        if len(cats) <= 1:
            category = cats[0] if cats else "news"
            return await self._fetch_with_event(
                {"id": f"google-{category}", "name": f"Google News · {category}", "category": category},
                limit,
            )
        return await self.fetch_categories(cats, limit)

    def _configured_sources(self) -> list[dict]:
        from src.repositories.source_repo import NewsSourceRepository

        repository = NewsSourceRepository(settings.database_url)
        stored = repository.list()
        if not stored:
            return []
        stored_by_id = {source["id"]: source for source in stored}
        defaults = [
            source.__dict__.copy()
            for source in self._default_sources()
            if source.id not in stored_by_id
        ]
        return [source for source in defaults if source["enabled"]] + [
            source for source in stored if source["enabled"]
        ]

    @staticmethod
    def _default_sources():
        from src.services.source_catalog import DEFAULT_SOURCES

        return DEFAULT_SOURCES

    async def fetch_sources(self, sources: list[dict], limit: int = 20) -> list[Article]:
        limit_each = max(1, limit // max(1, len(sources)))
        results = await asyncio.gather(
            *[
                self._fetch_with_event(source, limit_each)
                for source in sources
            ],
            return_exceptions=True,
        )
        articles: list[Article] = []
        seen_urls: set[str] = set()
        for source, result in zip(sources, results):
            if isinstance(result, BaseException):
                logger.warning("Skipping unavailable source %s", source["id"], exc_info=result)
                continue
            for article in result:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    articles.append(article)
        if not articles and results and all(isinstance(result, Exception) for result in results):
            raise ScrawlerError("All configured news sources failed")
        return articles

    async def _fetch_with_event(self, source: dict, limit: int) -> list[Article]:
        started = perf_counter()
        try:
            articles = await self.fetch_rss(
                limit,
                query=source.get("category") or source["name"],
                category=source.get("category"),
                source_url=source.get("url"),
                source_name=source["name"] if source.get("url") else None,
            )
        except ScrawlerError as exc:
            self.fetch_events.append(
                {
                    "source_id": source["id"],
                    "source_name": source["name"],
                    "category": source.get("category"),
                    "country": source.get("country") or settings.news_country,
                    "status": "failed",
                    "fetched_count": 0,
                    "latency_ms": round((perf_counter() - started) * 1000),
                    "error": type(exc).__name__,
                }
            )
            raise
        self.fetch_events.append(
            {
                "source_id": source["id"],
                "source_name": source["name"],
                "category": source.get("category"),
                "country": source.get("country") or settings.news_country,
                "status": "success",
                "fetched_count": len(articles),
                "latency_ms": round((perf_counter() - started) * 1000),
                "error": None,
            }
        )
        return articles

    def _configured_categories(self) -> list[str]:
        from src.repositories.config_repo import ConfigRepository

        override = ConfigRepository(settings.database_url).get("news_categories")
        if override:
            return [c.strip().lower() for c in override.split(",") if c.strip()]
        return settings.news_categories_list

    async def fetch_categories(self, categories: list[str], limit: int = 20) -> list[Article]:
        limit_each = max(1, limit // max(1, len(categories)))
        articles: list[Article] = []
        failures: list[ScrawlerError] = []
        for category in categories:
            try:
                articles.extend(
                    await self._fetch_with_event(
                        {
                            "id": f"google-{category}",
                            "name": f"Google News · {category}",
                            "category": category,
                        },
                        limit_each,
                    )
                )
            except ScrawlerError as exc:
                failures.append(exc)
                logger.warning("Skipping unavailable news category", exc_info=True)
        if failures and len(failures) == len(categories):
            raise ScrawlerError(
                "All news categories failed", retryable=any(e.retryable for e in failures)
            ) from failures[-1]
        return articles

    async def fetch_rss(
        self,
        limit: int = 20,
        query: str | None = None,
        category: str | None = None,
        source_url: str | None = None,
        source_name: str | None = None,
    ) -> list[Article]:
        q = query or category or "news"
        rss_url = source_url or f"https://news.google.com/rss/search?q={q}&hl=vi&gl=VN&ceid=VN:vi"
        if rss_url.startswith("google-news://"):
            google_query = rss_url.removeprefix("google-news://") or q
            country = settings.news_country.lower()
            language = "vi" if country == "vn" else "en"
            rss_url = f"https://news.google.com/rss/search?q={google_query}&hl={language}&gl={country}&ceid={country}:{language}"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(rss_url)
                resp.raise_for_status()
                text = resp.text
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise ScrawlerError(
                "RSS request rejected", retryable=status in (408, 429) or status >= 500
            ) from exc
        except httpx.RequestError as exc:
            raise ScrawlerError(
                "RSS transport failed",
                retryable=isinstance(
                    exc,
                    (
                        httpx.TimeoutException,
                        httpx.NetworkError,
                        httpx.RemoteProtocolError,
                        httpx.ProxyError,
                    ),
                ),
            ) from exc

        feed = feedparser.parse(text)
        if feed.bozo and not feed.entries:
            raise ScrawlerError("Invalid RSS response")
        articles: list[Article] = []
        for entry in feed.entries[:limit]:
            url = entry.get("link", "")
            title = entry.get("title", "")
            source = source_name or (
                entry.get("source", {}).get("title")
                if isinstance(entry.get("source"), dict)
                else None
            )
            article_id = hashlib.sha256(url.encode()).hexdigest()[:16] if url else ""
            published_at = _entry_datetime(entry)
            content = await self.extract_content(url) if url else None
            articles.append(
                Article(
                    id=article_id,
                    url=url,
                    title=title,
                    source=source,
                    category=category,
                    content=content,
                    fetched_at=datetime.utcnow(),
                    published_at=published_at,
                    summarized=0,
                )
            )
        return articles

    async def extract_content(self, url: str) -> str | None:
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded is None:
                return None
            content = trafilatura.extract(downloaded, include_links=True)
            if content:
                return content
            # fallback Readability is omitted for Stage 2 stub
            return None
        except (HTTPError, OSError):
            logger.warning("Article extraction unavailable; retaining title", exc_info=True)
            return None

    async def fetch_playwright_fallback(self, limit: int = 20) -> list[Article]:
        # Stage 2 stub: not implemented
        return []
