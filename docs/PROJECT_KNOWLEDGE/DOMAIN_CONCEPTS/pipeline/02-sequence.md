# 02 — Sequence Diagram

> Sequence diagram cho 1 pipeline run. Cập nhật 2026-09-04.

## Happy Path (success)

```mermaid
sequenceDiagram
    actor User
    participant Dashboard
    participant FastAPI
    participant Celery
    participant Worker
    participant Scrawler
    participant Synthesizer
    participant Messenger
    participant Telegram
    participant DB

    User->>Dashboard: Click "Run Now"
    Dashboard->>FastAPI: POST /api/runs
    FastAPI->>Celery: pipeline_run.delay()
    FastAPI-->>Dashboard: 202 {run_id, task_id}
    Dashboard-->>User: Show "Running..."

    Celery->>Worker: Pick up task
    Worker->>DB: INSERT pipeline_runs (status=running)

    Worker->>Scrawler: execute(limit)
    Scrawler->>Scrawler: Fetch RSS
    Scrawler->>Scrawler: Extract content
    Scrawler-->>Worker: List[Article]
    Worker->>DB: INSERT articles (dedup)

    Worker->>Synthesizer: execute(articles)
    Synthesizer->>Synthesizer: Build batch prompt
    Synthesizer->>Synthesizer: Call LLM
    Synthesizer-->>Worker: List[Summary]
    Worker->>DB: INSERT summaries
    Worker->>DB: UPDATE articles SET summarized=1

    alt telegram_enabled = true
        Worker->>Messenger: execute(summaries)
        Messenger->>Messenger: Format messages
        Messenger->>Telegram: send_message(...)
        Telegram-->>Messenger: 200 OK
        Messenger-->>Worker: success
    else telegram_enabled = false
        Worker->>Worker: Skip messenger
    end

    Worker->>DB: DELETE articles WHERE fetched_at < retention
    Worker->>DB: DELETE summaries WHERE created_at < retention
    Worker->>DB: UPDATE pipeline_runs SET status=success
    Worker-->>Celery: Task complete

    Note over Dashboard: Poll /api/runs every 5s
    Dashboard->>FastAPI: GET /api/runs
    FastAPI->>DB: SELECT pipeline_runs
    FastAPI-->>Dashboard: status=success
    Dashboard-->>User: Show "Success"
```

## Error Path (Scraper fail with retry)

```mermaid
sequenceDiagram
    participant Worker
    participant Scrawler
    participant DB

    Worker->>Scrawler: execute(limit)
    Scrawler->>Scrawler: Fetch RSS
    Scrawler--xWorker: httpx.TimeoutException
    Note over Worker: Retry 1/3 (wait 2s)

    Worker->>Scrawler: execute(limit)
    Scrawler--xWorker: httpx.TimeoutException
    Note over Worker: Retry 2/3 (wait 4s)

    Worker->>Scrawler: execute(limit)
    Scrawler-->>Worker: List[Article]
    Note over Worker: Continue normally
```

## Error Path (LLM fallback to raw titles)

```mermaid
sequenceDiagram
    participant Worker
    participant Synthesizer
    participant LLM
    participant DB

    Worker->>Synthesizer: execute(articles)
    Synthesizer->>LLM: chat.completions.create()
    LLM--xSynthesizer: openai.APIError (timeout)
    Note over Synthesizer: Retry 3x exhausted

    Synthesizer->>Synthesizer: Generate raw fallback
    Note over Synthesizer: summaries = title + URL<br/>for each article
    Synthesizer-->>Worker: List[Summary] (raw)
    Worker->>DB: INSERT summaries (model_used="raw_fallback")
```

## Dashboard Polling

```mermaid
sequenceDiagram
    actor User
    participant Dashboard
    participant FastAPI

    loop Every 5s
        Dashboard->>FastAPI: GET /api/runs
        FastAPI-->>Dashboard: [{run_id, status, ...}]
    end

    User->>Dashboard: Open page
    Dashboard->>FastAPI: GET /api/runs
    FastAPI-->>Dashboard: runs list
    Dashboard->>Dashboard: Render Timeline
```

## Trigger Sources

```mermaid
sequenceDiagram
    participant Source
    participant FastAPI
    participant Celery
    participant Worker

    alt Dashboard
        Source->>FastAPI: POST /api/runs
        FastAPI->>Celery: pipeline_run.delay()
    else GitHub Actions
        Note over Source: Run on ubuntu-latest<br/>không có Celery worker
        Source->>Source: python src/main.py
        Source->>Source: asyncio.run(pipeline.run())<br/>in-process, no Celery
    else Celery Beat
        Source->>Celery: pipeline_run.apply()
    end

    alt Celery path
        Celery->>Worker: Execute task
        Worker-->>Celery: Return result
    else Direct path (GA)
        Note over Source: Result written to SQLite<br/>dashboard đọc qua API
    end
```

## References

- [01-overview.md](01-overview.md) — stages, error handling
- [03-data-model.md](03-data-model.md) — DB schema
- [backend/04-pipeline.md](../backend/04-pipeline.md) — code
