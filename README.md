# ScrawlNews

Local Monitor Dashboard for news. The dashboard is the primary service running locally in one terminal; the newsbot pipeline (fetch, summarize, deliver via Telegram) is a feature toggle.

## Overview

ScrawlNews aggregates news from Google News RSS, extracts full content, summarizes via LLM, and delivers results. All operations are observable through a local dashboard with pipeline control, delivery monitoring, health checks, and analytics.

Pipeline:

```
Google News RSS -> Scrawler -> Articles -> Synthesizer -> Summaries -> Messenger (optional) -> Telegram
                       |                        |
                       v                        v
                  ArticleRepo              SummaryRepo
                       ^                        ^
                       +---- Dashboard (FastAPI + React) -- Celery/Redis ----+
                                Nginx :80 -> /api :8000, / :5173
```

## Stack

| Layer | Technology |
|-------|------------|
| Scrawler | Python, feedparser, Trafilatura, Readability-lxml, Playwright fallback |
| Synthesizer | OpenAI / OpenRouter / OmniRoute, gpt-4o-mini and free models |
| Messenger | Telegram Bot API, toggle via telegram_enabled |
| Dashboard Backend | FastAPI, Celery, Redis, SQLAlchemy, Pydantic Settings |
| Dashboard Frontend | React 18, TypeScript, Vite, Tailwind, shadcn/ui, TanStack Query, Recharts, SSE |
| Gateway | Nginx, reverse proxy /api to FastAPI and / to Vite |
| CLI | Go, Cobra, newsctl stub |
| Storage | SQLite file, pure local, mount ./data:/app/data |

## Quick Start

One terminal local hosting with Nginx parity for both Docker and non-Docker modes.

Docker (recommended):

```bash
docker compose up
# http://localhost
# http://localhost:8000/docs
```

Local without Docker (parity via Nginx in Docker):

```bash
make install
cp .env.example .env
make dev
# make dev starts nginx and redis in Docker plus uvicorn, celery worker, celery beat, vite concurrently
```

CLI pipeline still works without dashboard:

```bash
make run
python src/main.py --dry-run
```

Go stub:

```bash
go run ./cmd/newsctl --help
```

## Configuration

Configuration is loaded via Pydantic Settings from .env and injected into FastAPI and Celery.

Key variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| TELEGRAM_BOT_TOKEN | if TELEGRAM_ENABLED true | - | Telegram Bot token |
| TELEGRAM_CHAT_ID | if TELEGRAM_ENABLED true | - | Telegram chat or channel id |
| TELEGRAM_ENABLED | no | true | Toggle newsbot delivery feature |
| LLM_API_KEY | yes | - | OpenAI API key |
| OPENROUTER_API_KEY | no | - | OpenRouter or OmniRoute key |
| LLM_PROVIDER | no | openrouter | Provider name |
| LLM_MODEL | no | google/gemma-2-9b-it | Model name |
| FETCH_LIMIT | no | 20 | Max articles per run |
| SUMMARY_LANG | no | vi | Summary output language |
| RETENTION_DAYS | no | 7 | Data retention |
| LOG_LEVEL | no | INFO | Logging level |
| DATABASE_URL | no | sqlite:///data/scrawlnews.db | SQLite file, pure local |
| REDIS_URL | no | redis://localhost:6379/0 | Redis for Celery broker, docker uses redis://redis:6379/0 |
| CELERY_BROKER_URL | no | redis://localhost:6379/0 | Celery broker |
| CELERY_RESULT_BACKEND | no | redis://localhost:6379/1 | Celery result backend |

Hot reload is limited to fetch_limit, summary_lang, telegram_enabled, retention_days via PUT /api/config. Secrets and connection URLs require restart.

## Project Structure

```
ScrawlNews/
├── SKILL/                  # Agent skills, flat SKILL/<skill>/SKILL.md with tags
│   ├── README.md
│   ├── STRUCTURE.md
│   └── _template/
├── docs/plan/              # Planning docs
│   ├── INDEX.md
│   ├── PLAN.md
│   ├── IMPLEMENT.md
│   ├── decisions.md
│   ├── OPEN_QUESTIONS.md
│   └── spec/api.yaml
├── src/
│   ├── api/                # FastAPI dashboard
│   ├── worker/             # Celery Beat and Worker
│   ├── services/           # Scrawler, Synthesizer, Messenger
│   ├── repositories/       # Article, Summary, PipelineRun
│   ├── models/
│   └── config.py
├── web/                    # React Vite frontend
├── cmd/newsctl/            # Go Cobra stub
├── docker-compose.yml
├── nginx.conf
├── Makefile
└── data/                   # SQLite volume
```

## Documentation

* docs/plan/INDEX.md - reading guide and quick references
* docs/plan/PLAN.md - architecture, data model, configuration, deployment
* docs/plan/IMPLEMENT.md - technical implementation, testing, setup
* docs/plan/decisions.md - architecture decision records
* docs/plan/spec/api.yaml - OpenAPI 0.2.0 dashboard endpoints
* SKILL/README.md - skill organization research for Hermes and Claude
* SKILL/STRUCTURE.md - flat skill folder structure proposal

## Development

```bash
make install
make test          # BE pytest
cd web && npm run test   # FE Vitest
make lint
make typecheck
```

Tests cover both backend and frontend with coverage target above 80 percent. Database is pure local SQLite for all environments, no external service required.
