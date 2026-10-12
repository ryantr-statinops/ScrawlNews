# 04 — Pipeline

> Celery `pipeline.run` flow, data flow từ RSS → Telegram. Cập nhật 2026-09-04.

## Overview

```
Google News RSS
    │
    ▼
Scrawler.fetch() → List[Article]  (Celery task: pipeline.run)
    │
    ├── Save to ArticleRepo (dedup by URL hash)
    │
    ▼
Synthesizer.summarize(articles) → List[Summary]
    │
    ├── Save to SummaryRepo
    │
    ▼
Messenger.send(summaries) → Telegram Chat  (optional, telegram_enabled flag)
    │
    ▼
Cleanup: delete articles > retention_days
    │
    ▼
Update PipelineRun status (success/failed)
```

## Celery Task

```python
# src/worker/tasks.py
from celery import shared_task
from src.services.scrawler import ScrawlerService
from src.services.synthesizer import SynthesizerService
from src.services.messenger import MessengerService
from src.services.exceptions import ScrawlError
from src.config import settings

@shared_task(bind=True, max_retries=3, name="pipeline.run")
def pipeline_run(self, fetch_limit: int | None = None):
    """Run full pipeline: fetch → summarize → send."""
    log = get_task_logger(__name__)
    log.info("pipeline_started", fetch_limit=fetch_limit)

    try:
        limit = fetch_limit or settings.fetch_limit

        # 1. Fetch articles
        scrawler = ScrawlerService()
        articles = scrawler.execute(limit=limit)
        log.info("articles_fetched", count=len(articles))

        # 2. Save to DB (dedup)
        article_repo = ArticleRepository()
        for article in articles:
            article_repo.save(article)

        # 3. Summarize
        new_articles = article_repo.get_unsummarized(limit=limit)
        synthesizer = SynthesizerService()
        summaries = synthesizer.execute(new_articles)
        log.info("summaries_generated", count=len(summaries))

        # 4. Save summaries
        summary_repo = SummaryRepository()
        for summary in summaries:
            summary_repo.save(summary)
            article_repo.mark_summarized(summary.article_id)

        # 5. Send via Telegram (optional)
        telegram_sent = 0
        if settings.telegram_enabled:
            messenger = MessengerService()
            sent = messenger.execute(summaries)
            telegram_sent = 1 if sent else 0
            log.info("telegram_sent", sent=telegram_sent)

        # 6. Cleanup old data
        article_repo.cleanup_old(days=settings.retention_days)
        summary_repo.cleanup_old(days=settings.retention_days)

        log.info("pipeline_completed")
        return {"status": "success", "articles": len(articles), "summaries": len(summaries)}

    except ScrawlError as exc:
        log.exception("pipeline_failed", exc_info=exc)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

## Service Stages

### Stage 1: Scrawler

```python
# src/services/scrawler.py
class ScrawlerService(BaseService):
    async def execute(self, limit: int = 20) -> list[Article]:
        # 1. Fetch RSS feed
        feed = feedparser.parse(RSS_URL)
        entries = feed.entries[:limit]

        # 2. Extract content from each URL
        articles = []
        for entry in entries:
            try:
                content = await self._extract_content(entry.link)
                article = Article(
                    id=hashlib.sha256(entry.link.encode()).hexdigest()[:16],
                    url=entry.link,
                    title=entry.title,
                    source=entry.get("source", {}).get("title"),
                    content=content,
                    fetched_at=datetime.utcnow(),
                    summarized=0,
                )
                articles.append(article)
            except ScrawlerError:
                continue  # Skip individual failures, log via structlog

        return articles

    async def _extract_content(self, url: str) -> str:
        # Primary: Trafilatura
        # Fallback: Readability-lxml
        # Last resort: Playwright
        ...
```

### Stage 2: Synthesizer

```python
# src/services/synthesizer.py
class SynthesizerService(BaseService):
    async def execute(self, articles: list[Article]) -> list[Summary]:
        if not articles:
            return []

        try:
            prompt = self._build_prompt(articles)
            response = await self._call_llm(prompt)
            return self._parse_response(response, articles)
        except (openai.APIError, openai.RateLimitError) as exc:
            raise SynthesizerError(f"LLM call failed: {exc}") from exc

    async def _call_llm(self, prompt: str) -> str:
        # Use OpenAI client (works for OpenAI + OpenRouter)
        client = openai.AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        return response.choices[0].message.content
```

### Stage 3: Messenger (optional)

```python
# src/services/messenger.py
class MessengerService(BaseService):
    async def execute(self, summaries: list[Summary]) -> bool:
        if not settings.telegram_enabled:
            return False  # Skipped

        try:
            messages = self._format_messages(summaries)
            return await self._send_telegram(messages)
        except telegram.error.TelegramError as exc:
            raise MessengerError(f"Telegram send failed: {exc}") from exc

    async def _send_telegram(self, messages: list[str]) -> bool:
        bot = telegram.Bot(token=settings.telegram_bot_token)
        for msg in messages:
            try:
                await bot.send_message(
                    chat_id=settings.telegram_chat_id,
                    text=msg,
                    parse_mode="Markdown",
                )
            except telegram.error.RetryAfter as exc:
                await asyncio.sleep(exc.retry_after)
                await bot.send_message(...)  # retry once
            await asyncio.sleep(1)  # Rate limit
        return True
```

## Error Handling Flow

```
┌────────────────────────────────────────────────────────────┐
│                    Pipeline.run()                           │
└────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ Scrawler   │ │Synthesizer │ │ Messenger  │
       └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
             │             │              │
      ┌──────┴──────┐ ┌────┴────┐  ┌─────┴─────┐
      ▼             ▼ ▼         ▼  ▼           ▼
   Success      Retry(3x)   Fallback   Retry(3x)
      │             │         (raw)       │
      │         ┌───┴───┐         │   ┌───┴───┐
      │         ▼       ▼         ▼   ▼       ▼
      │      Success  Fail      Send   Success  Save local
      │         │       │         OK      │       file
      ▼         ▼       ▼         ▼       ▼       ▼
   Continue  Continue  Log &     Continue  Log &   Retry
   to next   to next   continue         next run
   stage     stage     to next
   stage     stage     stage
```

## Edge Cases

| Case | Detection | Handling |
|------|-----------|----------|
| Network timeout | `httpx.TimeoutException` | Retry 3x exponential backoff |
| HTTP 429/5xx | Response status | Retry với circuit breaker |
| Empty RSS feed | `len(articles) == 0` | Log warning, skip pipeline |
| LLM API error | `openai.APIError` | Fallback: raw titles + URLs |
| LLM rate limit | `openai.RateLimitError` | Queue, wait, retry |
| Telegram 429 | `RetryAfter` exception | Sleep `retry_after` seconds |
| Message > 4096 chars | `len(msg) > 4096` | Split tại `\n\n` boundaries |
| Duplicate article | `ArticleRepo.exists(url)` | Skip (INSERT OR IGNORE) |
| Content extract fail | `trafilatura` returns None | Skip article, continue |
| Config missing | Pydantic validation error | Exit với clear error |

## PipelineRun Tracking

```python
# src/repositories/run_repo.py
class PipelineRunRepository:
    def create(self, run_id: str, task_id: str) -> PipelineRun:
        """Create run record when task starts."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO pipeline_runs (id, status, task_id, started_at) VALUES (?, ?, ?, ?)",
                (run_id, "running", task_id, datetime.utcnow()),
            )
            conn.commit()

    def update(self, run_id: str, **fields) -> None:
        """Update run status (success/failed) and counts."""
        with self._connect() as conn:
            set_clause = ", ".join(f"{k} = ?" for k in fields)
            values = list(fields.values())
            values.append(run_id)
            conn.execute(f"UPDATE pipeline_runs SET {set_clause} WHERE id = ?", values)
            conn.commit()
```

## Trigger

```python
# src/api/routes/runs.py
@router.post("/api/runs", status_code=202)
def trigger_run(
    request: Request,
    fetch_limit: int | None = None,
    repo: PipelineRunRepository = Depends(get_run_repo),
):
    """Trigger pipeline.run, return task_id immediately."""
    task = pipeline_run.delay(fetch_limit)

    # Pre-create PipelineRun record
    run_id = str(uuid4())
    repo.create(run_id=run_id, task_id=task.id)

    return {"run_id": run_id, "task_id": task.id, "status": "pending"}
```

## References

- [02-architecture.md](02-architecture.md) — layered design
- [03-patterns.md](03-patterns.md) — error handling, retry
- [01-stack.md](01-stack.md) — Celery, Redis, tenacity
