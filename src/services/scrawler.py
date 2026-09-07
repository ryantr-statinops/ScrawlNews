import hashlib
from datetime import datetime

import feedparser
import httpx
import trafilatura

from src.config import settings
from src.models.article import Article
from src.services.base import BaseService


class ScrawlerService(BaseService):
    async def execute(
        self, limit: int = 20, categories: list[str] | None = None
    ) -> list[Article]:
        cats = categories or settings.news_categories_list
        if len(cats) <= 1:
            return await self.fetch_rss(limit, category=cats[0] if cats else None)
        return await self.fetch_categories(cats, limit)

    async def fetch_categories(self, categories: list[str], limit: int = 20) -> list[Article]:
        limit_each = max(1, limit // max(1, len(categories)))
        articles: list[Article] = []
        for category in categories:
            try:
                articles.extend(await self.fetch_rss(limit_each, category=category))
            except RuntimeError:
                continue
        return articles

    async def fetch_rss(
        self, limit: int = 20, query: str | None = None, category: str | None = None
    ) -> list[Article]:
        q = query or category or "news"
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=vi&gl=VN&ceid=VN:vi"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(rss_url)
                resp.raise_for_status()
                text = resp.text
        except Exception as e:
            raise RuntimeError(f"RSS fetch failed: {e}") from e

        feed = feedparser.parse(text)
        articles: list[Article] = []
        for entry in feed.entries[:limit]:
            url = entry.get("link", "")
            title = entry.get("title", "")
            source = (
                entry.get("source", {}).get("title")
                if isinstance(entry.get("source"), dict)
                else None
            )
            article_id = hashlib.sha256(url.encode()).hexdigest()[:16] if url else ""
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
        except Exception:
            return None

    async def fetch_playwright_fallback(self, limit: int = 20) -> list[Article]:
        # Stage 2 stub: not implemented
        return []
