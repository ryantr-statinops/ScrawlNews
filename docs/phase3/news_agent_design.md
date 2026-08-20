# Target Architecture

## System Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Scrawler   │────▶│  Synthesizer │────▶│  Messenger  │
│  Service    │     │  Service     │     │  Service    │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ ArticleRepo │     │ SummaryRepo  │     │ TelegramBot │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Data Model

- **Article**: id, url, title, source, raw_html, fetched_at
- **Summary**: id, article_id, summary_text, model_used, created_at

## Services

All services inherit from `BaseService` and implement `execute()`.
