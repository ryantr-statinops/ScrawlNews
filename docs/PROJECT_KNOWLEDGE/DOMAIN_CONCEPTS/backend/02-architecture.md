# 02 — Backend Architecture

> Folder structure, layered design, request flow. Cập nhật 2026-09-04.

## Layered Design

```
┌─────────────────────────────────────────────────────────────┐
│  HTTP Request                                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  API Layer (src/api/)                                        │
│  - FastAPI routes (articles, runs, config, ...)             │
│  - Request validation (Pydantic)                            │
│  - Dependency injection (Depends)                           │
│  - HTTP exception handling                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Service Layer (src/services/)                              │
│  - Business logic (Scrawler, Synthesizer, Messenger)        │
│  - BaseService abstract (execute method)                    │
│  - Domain exceptions (ScrawlerError, etc.)                  │
│  - Cross-cutting: retry (tenacity), logging (structlog)     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Repository Layer (src/repositories/)                       │
│  - Database access (sqlite3 raw SQL)                        │
│  - CRUD operations per entity                               │
│  - Deduplication, cleanup, migrations                       │
│  - Connection management                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Model Layer (src/models/)                                  │
│  - Pydantic schemas (Article, Summary, PipelineRun)         │
│  - Validation, serialization                                │
│  - Shared types                                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Database (SQLite file)                                     │
└─────────────────────────────────────────────────────────────┘
```

## Folder Structure (hiện tại + planned)

```
src/
├── __init__.py
├── main.py                 # Legacy CLI + Pipeline class
├── config.py               # Pydantic Settings (ADR-011)
├── models/
│   ├── __init__.py
│   ├── article.py          # Pydantic Article model
│   ├── summary.py          # Pydantic Summary model
│   └── run.py              # Pydantic PipelineRun model
├── services/
│   ├── __init__.py
│   ├── base.py             # BaseService abstract
│   ├── scrawler.py         # RSS fetch + extract
│   ├── synthesizer.py      # LLM batch
│   ├── messenger.py        # Telegram send
│   └── exceptions.py       # Custom exception classes (planned)
├── repositories/
│   ├── __init__.py
│   ├── article_repo.py     # Article CRUD
│   ├── summary_repo.py     # Summary CRUD
│   ├── run_repo.py         # PipelineRun CRUD
│   ├── config_repo.py      # Config persist + history
│   └── migrate.py          # Schema migrations
├── api/
│   ├── __init__.py
│   ├── main.py             # FastAPI app + exception handlers
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── articles.py     # GET /api/articles
│   │   ├── summaries.py    # GET /api/summaries
│   │   ├── runs.py         # GET/POST /api/runs, GET /api/tasks/{id}
│   │   ├── config.py       # GET/PUT /api/config, /api/config/history
│   │   ├── stats.py        # GET /api/stats
│   │   ├── logs.py         # GET /api/logs/stream (SSE)
│   │   └── health.py       # GET /health, /live, /ready
│   └── deps.py             # FastAPI dependencies
├── worker/
│   ├── __init__.py
│   ├── celery_app.py       # Celery app config
│   └── tasks.py            # pipeline_run task
└── utils/
    ├── __init__.py
    ├── retry.py            # tenacity helpers
    ├── formatter.py        # Message formatting
    └── logging.py          # structlog config (planned)
```

## Request Flow (HTTP)

```
1. Client → Nginx (:80)
   - HTTP Basic auth check (if .htpasswd mounted)
   - Rate limit (if Nginx limit_req configured)
   - Proxy to FastAPI (:8000)

2. Nginx → FastAPI
   - Match route → handler
   - Validate request body/query (Pydantic)
   - Resolve dependencies (Depends)

3. FastAPI → Service
   - Service.execute(args)
   - Domain logic
   - May throw ScrawlError

4. Service → Repository
   - CRUD operations
   - May throw NotFoundError / RepositoryError

5. Repository → SQLite
   - Raw SQL via sqlite3
   - Return rows → Pydantic models

6. Response flow (reverse)
   - Pydantic model → JSON
   - Exception → HTTP status (via handler)
   - Slowapi rate limit check
   - Nginx → Client
```

## Background Task Flow (Celery)

```
1. FastAPI receives POST /api/runs
   - Returns 202 with task_id immediately
   - pipeline_run.delay(fetch_limit)

2. Celery worker picks up task
   - Deserialize args
   - Run pipeline_run function
   - Max retries 3 with exponential backoff

3. Pipeline executes services
   - Scrawler → Synthesizer → Messenger
   - Each stage logged via structlog
   - Errors caught + saved to PipelineRun.error

4. Result backend stores task state
   - Redis: success/failure/result
   - FastAPI can poll /api/tasks/{task_id}
   - Frontend polls /api/runs every 5s
```

## Dependency Injection (FastAPI Depends)

```python
# src/api/deps.py
from fastapi import Depends
from src.config import Settings, settings

def get_settings() -> Settings:
    return settings

def get_article_repo(
    settings: Settings = Depends(get_settings),
) -> ArticleRepository:
    return ArticleRepository(settings.database_url)

# src/api/routes/articles.py
@router.get("/api/articles")
def list_articles(
    q: str | None = None,
    source: str | None = None,
    repo: ArticleRepository = Depends(get_article_repo),
):
    return repo.list(q=q, source=source)
```

## Request/Response Models

```python
# src/models/article.py
from pydantic import BaseModel, Field

class Article(BaseModel):
    id: str = Field(..., description="SHA256(url)[:16]")
    url: str
    title: str
    source: str | None = None
    content: str | None = None
    fetched_at: datetime
    summarized: int = 0

class ArticleList(BaseModel):
    count: int
    articles: list[Article]
```

## Layer Responsibilities

| Layer | Responsibility | Don't |
|-------|----------------|------|
| **API** | HTTP, validation, DI, status codes | Business logic, DB access |
| **Service** | Business logic, orchestration, retries | HTTP, DB queries |
| **Repository** | DB queries, data mapping | Business logic, HTTP |
| **Model** | Schema, validation, serialization | DB access, business logic |

## References

- [01-stack.md](01-stack.md) — library choices
- [03-patterns.md](03-patterns.md) — BaseService, Repository, error patterns
- [04-pipeline.md](04-pipeline.md) — Celery task flow
