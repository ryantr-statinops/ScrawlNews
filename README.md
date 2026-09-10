# ScrawlNews

Local Monitor Dashboard for news. The dashboard is the primary service running locally in one terminal; the newsbot pipeline (fetch, summarize, deliver via Telegram) is a feature toggle.

## Overview

ScrawlNews aggregates news from Google News RSS and custom RSS/Atom sources, extracts full content, summarizes via LLM, and delivers results. All operations are observable through a local dashboard with pipeline control, delivery monitoring, health checks, and an Analytics Command Center.

Pipeline:

```
Google News RSS -> Scrawler -> Articles -> Synthesizer -> Summaries -> Messenger (optional) -> Telegram
                       |                        |
                       v                        v
                  ArticleRepo              SummaryRepo
                       ^                        ^
                       +---- Dashboard (FastAPI + React) -- Celery/Redis ----+
                                Nginx :6767 -> /api :8000, / :5173
```

## Stack

| Layer | Technology |
|-------|------------|
| Scrawler | Python, feedparser, Trafilatura, Readability-lxml, Playwright fallback |
| Synthesizer | OpenAI / OpenRouter / OmniRoute, gpt-4o-mini and free models |
| Messenger | Telegram Bot API, toggle via telegram_enabled |
| Dashboard Backend | FastAPI, Celery, Redis, sqlite3 (stdlib, raw SQL), Pydantic Settings |
| Dashboard Frontend | React 18, TypeScript, Vite, Mantine UI v7, TanStack Router, TanStack Query, ApexCharts, Zustand, SSE (xem [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/01-stack.md](docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/01-stack.md)) |
| Gateway | Nginx, reverse proxy /api to FastAPI and / to Vite |
| CLI | Go, Cobra, newsctl stub |
| Storage | SQLite file, pure local, mount ./data:/app/data |

## Quick Start

One terminal local hosting with Nginx parity for both Docker and non-Docker modes.

Docker (recommended):

```bash
docker-compose up -d --build
# http://localhost:6767
# http://localhost:8000/docs
```

Telegram is optional for the local dashboard. Set `TELEGRAM_ENABLED=false` in
`.env` when no valid Telegram bot credentials are available.

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
| NEWS_CATEGORIES | no | technology,business,world,science | RSS categories, comma-separated |
| SCHEDULE_INTERVAL_HOURS | no | 24 | Briefing interval for beat scheduler |
| SCHEDULE_TIMES | no | 08:00,12:00,18:00 | Daily run times, comma-separated HH:MM |
| SCHEDULE_TIMEZONE | no | Asia/Ho_Chi_Minh | Timezone for scheduled runs |
| NEWS_COUNTRY | no | VN | Google News country locale |
| NEWS_CITY | no | Hanoi | Display/configuration city |
| LOG_LEVEL | no | INFO | Logging level |
| DATABASE_URL | no | sqlite:///data/scrawlnews.db | SQLite file, pure local |
| REDIS_URL | no | redis://localhost:6379/0 | Redis for Celery broker, docker uses redis://redis:6379/0 |
| CELERY_BROKER_URL | no | redis://localhost:6379/0 | Celery broker |
| CELERY_RESULT_BACKEND | no | redis://localhost:6379/1 | Celery result backend |

Hot reload supports fetch_limit, summary_lang, telegram_enabled, retention_days, news_categories, schedule_times, schedule_timezone, news_country and news_city via PUT /api/config. Secrets and connection URLs require restart.

## Feed workflow

Feed is the main local dashboard. Use **Update feed** to run the pipeline without opening Runs, filter articles by query/category/source/date, and open an article row for extracted content, published/fetched timestamps and related summaries. The workspace places the Agent mock and Topic digests in the left utility rail, with the article table on the right at desktop widths; it becomes a single-column layout on mobile. The Agent is frontend-only mock mode with local message input and a collapse/expand control; its collapsed state keeps a 48px header and 16px spacing before Topic digests. Settings contains the fetch limit, schedule, locale, health and source manager. Sources are RSS/Atom URLs from the built-in catalog or user-added feeds; the Source Manager can test and enable/disable them. Topic digests are generated per category after a successful run when summaries are available and open in a left-side detail drawer with source articles and history.

## Analytics Command Center

Analytics has five workspaces sharing a `1h`–`30d` time window and category, source, provider and model filters:

- **Overview** — current-vs-previous KPI, operational alerts, news velocity and category/source snapshots.
- **Content** — category movement, source diversity and article freshness.
- **Pipeline** — run success, throughput, median/P95 timing and stage errors.
- **Sources** — fetch health, article yield, duplicate rate and latency by source.
- **AI Usage** — input/output/total tokens, request failures and latency by provider, model and operation.

Analytics filters are reflected in the URL. KPI, table and chart drill-downs open records in place and link to Feed or Runs where applicable. Pipeline, source-fetch and LLM telemetry is best-effort and retained for 30 days independently of article retention. Historical articles created before telemetry migration still appear in Content totals, but historical stage/source/LLM measurements cannot be reconstructed.

## Project Structure

```
ScrawlNews/
├── .agent/SKILL/           # Agent skills, flat .agent/SKILL/<skill>/SKILL.md with tags
│   ├── README.md
│   ├── STRUCTURE.md
│   ├── _template/
│   └── commit-workflow/
├── docs/                  # Knowledge, execution, guides (see docs/README.md)
│   ├── README.md
│   ├── PROJECT_KNOWLEDGE/  # current state, target arch, decisions, domain concepts
│   ├── EXECUTION/          # active plans, tasks, completed, archived
│   └── GUIDES/             # setup, testing, deployment
├── src/
│   ├── api/                # FastAPI dashboard
│   ├── worker/             # Celery Beat and Worker + dynamic scheduler
│   ├── services/           # Scrawler, Synthesizer, Messenger, Telegram Bot
│   ├── repositories/       # Article, Summary, PipelineRun, Config
│   ├── models/
│   └── config.py
├── frontend/               # React Vite dashboard (Mantine + TanStack Router)
├── cmd/newsctl/            # Go Cobra stub
├── docker-compose.yml
├── docker-compose.dev.yml  # Dev override (nginx host routing)
├── nginx.conf
├── nginx.dev.conf          # Dev nginx (host.docker.internal)
├── Makefile
└── data/                   # SQLite volume
```

## Documentation

* docs/README.md - documentation map and reading guide
* docs/PROJECT_KNOWLEDGE/CURRENT_STATE.md - what is actually built and verified
* docs/PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md - target architecture
* docs/PROJECT_KNOWLEDGE/DECISIONS.md - architecture decision records (ADRs)
* docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/ - core concepts per responsibility
* docs/EXECUTION/ACTIVE_PLANS/roadmap.md - roadmap (stages)
* docs/EXECUTION/ACTIVE_PLANS/specs/api.yaml - OpenAPI 0.2.0 dashboard endpoints
* docs/GUIDES/setup.md - setup and usage
* docs/GUIDES/testing.md - testing strategy
* docs/GUIDES/deployment.md - deployment (GitHub Actions, Docker, Nginx)
* .agent/SKILL/README.md - skill organization research for Hermes and Claude
* .agent/SKILL/STRUCTURE.md - flat skill folder structure proposal

## Development

```bash
make install
make test          # BE pytest
cd frontend && npm run test   # FE Vitest
make lint
make typecheck
```

Tests cover both backend and frontend with coverage target above 80 percent. Database is pure local SQLite for all environments, no external service required.
