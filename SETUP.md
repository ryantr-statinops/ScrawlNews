# Setup Guide

## Prerequisites
- Python 3.11+
- Node 20+
- Docker and Docker Compose
- Git

## Quick Start

```bash
git clone https://github.com/ryantr-statinops/ScrawlNews.git
cd ScrawlNews
make install
cp .env.example .env
# edit .env with LLM_API_KEY, TELEGRAM_BOT_TOKEN if needed
docker compose up
# http://localhost
# http://localhost:8000/docs
```

Local without Docker (parity via Nginx in Docker):

```bash
make install
cp .env.example .env
make dev
```

## Environment

See .env.example for DATABASE_URL pure local, REDIS_URL, CELERY_*, TELEGRAM_ENABLED, LLM_*

Hot reload limited to fetch_limit, summary_lang, telegram_enabled, retention_days via PUT /api/config.

## CLI

```bash
make run
python src/main.py --dry-run --limit 10
go run ./cmd/newsctl --help
```

## Verification

```bash
docker compose config --quiet
docker compose build
pytest tests/ --cov=src
cd web && npm run test
ruff check src/
```

See docs/README.md for reading guide and documentation map.
