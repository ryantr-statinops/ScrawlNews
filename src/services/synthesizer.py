import logging
import uuid
from datetime import datetime
from time import perf_counter

from openai import APIConnectionError, APIStatusError, AsyncOpenAI

from src.config import settings
from src.models.article import Article
from src.models.summary import Summary
from src.repositories.telemetry_repo import TelemetryRepository
from src.services.base import BaseService
from src.utils.circuit_breaker import CircuitBreaker
from src.utils.errors import ConfigError, SynthesizerError

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a news summarizer. Given a list of news articles,
create a concise daily briefing in Vietnamese with:
1. Top 3-5 most important stories
2. 1-2 sentences per story
3. Keep it scannable
"""

_llm_breaker = CircuitBreaker("llm", failure_threshold=5, cooldown_seconds=60)


class SynthesizerService(BaseService):
    def __init__(self):
        api_key = settings.openrouter_api_key or settings.llm_api_key
        base_url = "https://openrouter.ai/api/v1" if settings.llm_provider == "openrouter" else None
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url) if api_key else None

    async def execute(self, articles: list[Article], run_id: str | None = None) -> list[Summary]:
        if not articles:
            return []
        if not self.client:
            # fallback raw titles
            return self._fallback(articles)
        prompt = self.build_prompt(articles)
        try:
            text = await self.call_llm(prompt, operation="article_summary", run_id=run_id)
        except SynthesizerError:
            logger.warning("Summarization unavailable; retaining titles", exc_info=True)
            return self._fallback(articles)
        return self.parse_response(text, articles)

    def build_prompt(self, articles: list[Article]) -> str:
        articles_text = "\n".join(
            [f"- {a.title} ({a.url}): {a.content[:500] if a.content else ''}" for a in articles]
        )
        return f"{SYSTEM_PROMPT}\n\nSummarize these articles:\n{articles_text}\n\nRequirements: Vietnamese, 150-250 words, include source."

    async def call_llm(
        self, prompt: str, operation: str = "article_summary", run_id: str | None = None
    ) -> str:
        if self.client is None:
            raise ConfigError("LLM credentials are missing")
        if not _llm_breaker.allow_request():
            raise SynthesizerError("LLM circuit breaker is open", retryable=False)
        started = perf_counter()
        try:
            resp = await self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
            )
        except APIConnectionError as exc:
            _llm_breaker.record_failure()
            self._record_usage(operation, run_id, started, "failed", error="APIConnectionError")
            raise SynthesizerError("LLM transport failed", retryable=True) from exc
        except APIStatusError as exc:
            _llm_breaker.record_failure()
            self._record_usage(operation, run_id, started, "failed", error="APIStatusError")
            raise SynthesizerError(
                "LLM request rejected",
                retryable=exc.status_code in (408, 409, 429) or exc.status_code >= 500,
            ) from exc
        if not resp.choices or not resp.choices[0].message.content:
            _llm_breaker.record_failure()
            self._record_usage(operation, run_id, started, "failed", error="EmptyResponse")
            raise SynthesizerError("LLM returned no summary")
        _llm_breaker.record_success()
        usage = resp.usage
        self._record_usage(
            operation,
            run_id,
            started,
            "success",
            input_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            total_tokens=getattr(usage, "total_tokens", 0) if usage else 0,
        )
        return resp.choices[0].message.content

    def _record_usage(
        self,
        operation: str,
        run_id: str | None,
        started: float,
        status: str,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
        error: str | None = None,
    ) -> None:
        try:
            TelemetryRepository(settings.database_url).record_llm_usage(
                run_id=run_id,
                operation=operation,
                provider=settings.llm_provider,
                model=settings.llm_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                latency_ms=round((perf_counter() - started) * 1000),
                status=status,
                error=error,
            )
        except Exception:
            logger.warning("Unable to record LLM telemetry", exc_info=True)

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
