import uuid
from datetime import datetime

from openai import AsyncOpenAI

from src.config import settings
from src.models.article import Article
from src.models.summary import Summary
from src.services.base import BaseService

SYSTEM_PROMPT = """You are a news summarizer. Given a list of news articles,
create a concise daily briefing in Vietnamese with:
1. Top 3-5 most important stories
2. 1-2 sentences per story
3. Keep it scannable
"""


class SynthesizerService(BaseService):
    def __init__(self):
        api_key = settings.openrouter_api_key or settings.llm_api_key
        base_url = "https://openrouter.ai/api/v1" if settings.llm_provider == "openrouter" else None
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url) if api_key else None

    async def execute(self, articles: list[Article]) -> list[Summary]:
        if not articles:
            return []
        if not self.client:
            # fallback raw titles
            return self._fallback(articles)
        try:
            prompt = self.build_prompt(articles)
            text = await self.call_llm(prompt)
            return self.parse_response(text, articles)
        except Exception:
            return self._fallback(articles)

    def build_prompt(self, articles: list[Article]) -> str:
        articles_text = "\n".join(
            [f"- {a.title} ({a.url}): {a.content[:500] if a.content else ''}" for a in articles]
        )
        return f"{SYSTEM_PROMPT}\n\nSummarize these articles:\n{articles_text}\n\nRequirements: Vietnamese, 150-250 words, include source."

    async def call_llm(self, prompt: str) -> str:
        resp = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        return resp.choices[0].message.content or ""

    def parse_response(self, response: str, articles: list[Article]) -> list[Summary]:
        # Stage 2 stub: one summary per article from response chunks
        summaries: list[Summary] = []
        for a in articles:
            summaries.append(
                Summary(
                    id=str(uuid.uuid4()),
                    article_id=a.id,
                    summary_text=response[:500] if response else a.title,
                    model_used=settings.llm_model,
                    created_at=datetime.utcnow(),
                )
            )
        return summaries

    def _fallback(self, articles: list[Article]) -> list[Summary]:
        return [
            Summary(
                id=str(uuid.uuid4()),
                article_id=a.id,
                summary_text=a.title,
                model_used="fallback",
                created_at=datetime.utcnow(),
            )
            for a in articles
        ]
