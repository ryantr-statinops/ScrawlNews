# Pipeline (Data Flow)

> Tài liệu pipeline end-to-end: sequence, data model, performance dashboard.

## Index

- [01-overview.md](01-overview.md) — Tổng quan pipeline, stages, error handling flow
- [02-sequence.md](02-sequence.md) — Sequence diagram cho mỗi run, từ trigger → Telegram
- [03-data-model.md](03-data-model.md) — ER diagram cho DB schema, relations giữa Article/Summary/PipelineRun/Config
- [04-performance.md](04-performance.md) — Dashboard metrics: timing, cost, resource, scaling

## Tổng quan

Pipeline chạy qua 3 stage chính:

```
RSS → Scrawler → Articles → Synthesizer → Summaries → Messenger (optional) → Telegram
         │              │                  │              │
         ▼              ▼                  ▼              ▼
    ArticleRepo    dedup SHA256      SummaryRepo    Telegram Bot
```

Trigger: dashboard `POST /api/runs` hoặc GitHub Actions cron 4 lần/ngày.

## Reading guide

| Bạn muốn biết… | Đọc file |
|---|---|
| Pipeline chạy thế nào, stages, errors | [01-overview.md](01-overview.md) |
| Trigger → execute flow, timeline | [02-sequence.md](02-sequence.md) |
| DB schema, tables, relations | [03-data-model.md](03-data-model.md) |
| Timing, cost, resource estimates | [04-performance.md](04-performance.md) |

## Status

Cập nhật: 2026-09-04. Phase 3 docs DRAFT.

## References

- [backend/04-pipeline.md](../backend/04-pipeline.md) — code-level pipeline
- [backend/02-architecture.md](../backend/02-architecture.md) — layered design
- [DECISIONS.md](../../DECISIONS.md) — ADR-011/012
