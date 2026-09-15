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
                                Client :6767 -> /api :8000, / :5173
                                Dagster Operations :6768 -> Dagster webserver :3000
```

## Stack

| Layer | Technology |
|-------|------------|
| Scrawler | Python, feedparser, Trafilatura, Readability-lxml, Playwright fallback |
| Synthesizer | OpenAI / OpenRouter / OmniRoute, gpt-4o-mini and free models |
| Messenger | Telegram Bot API, toggle via telegram_enabled |
| Dashboard Backend | FastAPI, Celery, Redis, sqlite3 (stdlib, raw SQL), Pydantic Settings |
| Dashboard Frontend | React 18, TypeScript, Vite, Mantine UI v7, TanStack Router, TanStack Query, ApexCharts, Zustand, SSE (xem [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/01-stack.md](docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/01-stack.md)) |
| Operations UI | Dagster 1.13.22, isolated shadow assets and SQLite instance storage |
| Gateway | Client gateway on 6767; Dagster webserver on 6768 |
| CLI | Go, Cobra, newsctl stub |
| Storage | SQLite file, pure local, mount ./data:/app/data |

## Quick Start

One terminal local hosting with Nginx parity for both Docker and non-Docker modes.

Docker (recommended):

```bash
docker-compose up -d --build
# Client Product: http://localhost:6767
# Dagster Operations: http://localhost:6768
# http://localhost:8000/docs
```

Dagster currently runs as an isolated shadow operations surface. Celery and
Celery Beat remain the production pipeline; Dagster shadow assets do not send
Telegram messages or write to the domain SQLite database. Open `http://localhost:6768`
for asset graph, runs, logs and retries.

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
python -m src.main --dry-run
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
| DAGSTER_SHADOW_DB_URL | no | sqlite:///data/dagster-shadow/shadow.db | Per-run shadow SQLite namespace |
| DAGSTER_SHADOW_LIMIT | no | 20 | Shadow fetch limit |
| DAGSTER_SHADOW_CATEGORIES | no | technology | Shadow categories, comma-separated |

Hot reload supports fetch_limit, summary_lang, telegram_enabled, retention_days, news_categories, schedule_times, schedule_timezone, news_country and news_city via PUT /api/config. Secrets and connection URLs require restart; the config API returns only configured/not-configured state.

## Feed workflow

Feed is the main local dashboard. Use **Update feed** to fetch articles, filter by query/category/source/date, and open an article for extracted content, published/fetched timestamps and related summaries. Topic digests, Telegram delivery and preferences stay in the Client Product UI. The workspace becomes a single-column layout on mobile. Operations details stay at `:6768` in Dagster.

## Analytics Command Center

Analytics has four Client workspaces sharing a `1h`–`30d` time window and category, source, provider and model filters:

- **Overview** — current-vs-previous KPI, operational alerts, news velocity and category/source snapshots.
- **Content** — category movement, source diversity and article freshness.
- **Sources** — fetch health, article yield, duplicate rate and latency by source.
- **Model analytics** — input/output/total tokens, request failures and latency by provider, model and activity.

Analytics filters are reflected in the URL. KPI, table and chart drill-downs open records in place. Source-fetch and LLM telemetry is best-effort and retained for 30 days independently of article retention. Historical articles created before telemetry migration still appear in Content totals, but historical stage/source/LLM measurements cannot be reconstructed.

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
