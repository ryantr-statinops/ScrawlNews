# ScrawlNews

ScrawlNews is a local-first news-monitoring dashboard. It collects configured RSS/Atom and Google News feeds, extracts article content, generates LLM summaries and category digests, and can optionally deliver results through Telegram.

## Start

- [Setup and first run](SETUP.md)
- [Project documentation](docs/README.md)
- [Product overview](docs/product/overview.md)

For the standard Docker Compose stack, the Client is at `http://localhost:6767`, FastAPI at `http://localhost:8000/docs`, and the Dagster shadow UI at `http://localhost:6768`.

```bash
cp .env.example .env
# Set TELEGRAM_ENABLED=false unless Telegram delivery is intended and configured.
docker compose up -d --build
```

The standard Compose stack uses Celery/Beat for production pipeline execution. Dagster is a separate shadow surface; it does not replace the Celery scheduler or send Telegram messages.

## Current boundaries

- Local SQLite is the domain store; Redis coordinates Celery.
- Supported ingestion is configured RSS/Atom plus Google News category feeds. Complete Hacker News/Reddit adapters are not present.
- LLM keys are needed for summarization runs, not for opening the dashboard.
- The repository contains local Compose, CI, and scheduled non-delivery smoke workflows; it does not publish a hosted application deployment.

Read [docs/README.md](docs/README.md) for architecture, API/configuration, operations, and dated verification history. Check the live Git state and CI before treating a historical report as current.
