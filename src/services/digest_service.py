import uuid
from datetime import datetime

from src.config import settings
from src.models.article import Article
from src.models.digest import Digest
from src.models.summary import Summary
from src.services.synthesizer import SynthesizerService


class DigestService:
    def __init__(self):
        self.synthesizer = SynthesizerService()

    async def execute(
        self,
        category: str,
        articles: list[Article],
        summaries: list[Summary],
        run_id: str | None = None,
    ) -> Digest:
        summary_text = "\n".join(f"- {item.summary_text}" for item in summaries)
        fallback = "\n".join(f"- {article.title}" for article in articles)
        digest_text = fallback
        model = "fallback"
        status = "ready"
        error = None
        if self.synthesizer.client and summaries:
            try:
                digest_text = await self.synthesizer.call_llm(
                    f"Create a concise Vietnamese news digest for the {category} topic.\n"
                    f"Summaries:\n{summary_text}\nLimit to 5 key points.",
                    operation="topic_digest",
                    run_id=run_id,
                )
                model = settings.llm_model
            except Exception:
                status = "error"
                error = "Digest generation unavailable"
        return Digest(
            id=str(uuid.uuid4()),
            category=category,
            title=f"{category.title()} briefing",
            digest_text=digest_text,
            article_count=len(articles),
            model_used=model,
            status=status,
            error=error,
            created_at=datetime.utcnow(),
        )
