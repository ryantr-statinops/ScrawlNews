# 01 — Pipeline Overview

> Tổng quan pipeline end-to-end: stages, error handling, retry. Cập nhật 2026-09-04.

## Stages

Pipeline gồm 3 services chạy tuần tự trong 1 Celery task `pipeline.run`:

| # | Stage | Service | Input | Output | Optional |
|---|-------|---------|-------|--------|----------|
| 1 | **Scrawler** | `ScrawlerService` | RSS URL | `List[Article]` | No |
| 2 | **Synthesizer** | `SynthesizerService` | `List[Article]` | `List[Summary]` | No |
| 3 | **Messenger** | `MessengerService` | `List[Summary]` | Telegram messages | Yes (toggle) |

## Data Flow

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│   RSS   │───▶│Scrawler │───▶│Articles │───▶│Synthesi │───▶│Summaries│
│ Google  │    │ Service │    │  (DB)   │    │  zer    │    │  (DB)   │
│  News   │    │ fetch   │    │ dedup   │    │  LLM    │    │         │
└─────────┘    │ extract │    │ SHA256  │    │ batch   │    └────┬────┘
               └─────────┘    └─────────┘    └─────────┘         │
                                                │                │
                                                ▼                ▼
                                          ┌─────────┐    ┌─────────┐
                                          │ Fallback│    │Messenger│
                                          │ raw     │    │ (toggle)│
                                          │ titles  │    │ Telegram│
                                          └─────────┘    └─────────┘
```

## Error Handling Flow

```
Pipeline.run() invoked
        │
        ▼
   ┌─────────┐
   │ Scrawler │──── fail ──▶ Retry 3x (tenacity, exp backoff)
   └────┬─────┘                    │
        │ success                  │ exhausted
        ▼                          ▼
   Save to ArticleRepo        Mark run failed
   (INSERT OR IGNORE)         (PipelineRun.error)
        │
        ▼
   ┌─────────────┐
   │ Synthesizer │──── fail ──▶ Retry 3x
   └──────┬──────┘             │
          │ success            │ exhausted
          ▼                    ▼
     Save SummaryRepo     Fallback: raw titles
     mark_summarized      (vẫn save "summary" = title)
          │
          ▼
   ┌──────────┐
   │ Messenger │──── telegram_enabled=false ──▶ Skip (return 0)
   └─────┬────┘
         │ true
         ▼
   Send Telegram
   (RetryAfter → sleep, retry)
         │
         ▼
   Cleanup (retention_days)
         │
         ▼
   PipelineRun.status = success
```

## Retry Policy

| Layer | Retry | Backoff | Max time | Scope |
|-------|-------|---------|----------|-------|
| Scrawler (network) | 3x | 2s → 4s → 8s | ~14s | Per-call (HTTP) |
| Synthesizer (LLM) | 3x | 2s → 4s → 8s | ~14s | **Per-batch** (fail 1 batch = retry; fail 1 article = skip + log) |
| Messenger (Telegram) | 1x | On `RetryAfter` | varies | Per-message |
| Pipeline.run (overall) | 3x | 2s → 4s → 8s | ~14s + stage time | Per-task (Celery) |

## Edge Cases

| Case | Detection | Handling |
|------|-----------|----------|
| Empty RSS feed | `len(articles) == 0` | Log warning, skip pipeline |
| All duplicates | `rowcount == 0` | Skip summarize, send empty |
| LLM timeout | `httpx.TimeoutException` | Retry, fallback raw |
| LLM rate limit | `openai.RateLimitError` | Sleep + retry |
| Telegram 429 | `telegram.error.RetryAfter` | Sleep `retry_after` |
| Message > 4096 | `len(msg) > 4096` | Split at `\n\n` |
| Telegram disabled | `telegram_enabled=false` | Skip stage |
| Config missing | Pydantic validation | Exit with error |

## Trigger Sources

1. **Dashboard** — `POST /api/runs` (manual, user clicks "Run Now")
2. **GitHub Actions** — cron `0 8,12,16,21 * * *` (4x daily, production)
3. **Celery Beat** — local scheduler (dev only)
4. **Legacy CLI** — `python src/main.py --dry-run`

## PipelineRun Lifecycle

| Status | When | Set by |
|--------|------|--------|
| `pending` | Task queued, worker not picked up | Celery (auto) |
| `running` | Worker started | Celery task `on_start` |
| `success` | All stages completed | Task body |
| `failed` | Exception not caught | Task body / retry exhaustion |

## References

- [02-sequence.md](02-sequence.md) — sequence diagram
- [03-data-model.md](03-data-model.md) — ER diagram
- [04-performance.md](04-performance.md) — dashboard metrics
- [backend/04-pipeline.md](../backend/04-pipeline.md) — code detail
