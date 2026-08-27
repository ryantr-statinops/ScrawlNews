import hashlib
import httpx
import feedparser
import trafilatura
from datetime import datetime
from src.services.base import BaseService
from src.models.article import Article
from src.config import settings


class ScrawlerService(BaseService):
    async def execute(self, limit: int = 20) -> list[Article]:
        return await self.fetch_rss(limit)

    async def fetch_rss(self, limit: int = 20) -> list[Article]:
        rss_url = f"https://news.google.com/rss/search?q=news&hl=vi&gl=VN&ceid=VN:vi"
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
            source = entry.get("source", {}).get("title") if isinstance(entry.get("source"), dict) else None
            article_id = hashlib.sha256(url.encode()).hexdigest()[:16] if url else ""
            content = await self.extract_content(url) if url else None
            articles.append(
                Article(
                    id=article_id,
                    url=url,
                    title=title,
                    source=source,
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
