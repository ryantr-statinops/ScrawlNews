# Backend (FastAPI + Celery + Redis)

> Tài liệu backend stack, architecture, patterns, pipeline, config, testing.

## Index

- [01-stack.md](01-stack.md) — Tech stack + lý do chọn (Python 3.11, FastAPI, Celery, Redis, sqlite3, structlog, slowapi)
- [02-architecture.md](02-architecture.md) — Layered architecture (api → services → repos → models), folder structure
- [03-patterns.md](03-patterns.md) — BaseService, Repository, DI, error handling, retry, logging
- [04-pipeline.md](04-pipeline.md) — Celery `pipeline.run` flow, data flow, error handling per stage
- [05-config.md](05-config.md) — Pydantic Settings, hot-reload, env validation, secrets
- [06-testing.md](06-testing.md) — Pytest fixtures, mocking, coverage, CI

## Stack nhanh

| Layer | Library |
|-------|---------|
| Runtime | Python 3.11 |
| Web framework | FastAPI 0.110 + Uvicorn |
| Task queue | Celery 5.3 + Redis 5.0 (broker + result backend) |
| Scheduler | Celery Beat |
| Database | SQLite (file-based, mount `./data`) |
| DB access | sqlite3 stdlib (raw SQL) |
| Validation | Pydantic 2 + pydantic-settings |
| Logging | structlog (JSON to stdout) |
| Retry | tenacity |
| HTTP client | httpx (async) |
| Rate limit | slowapi (per-IP) |
| Testing | pytest + pytest-asyncio + pytest-cov |
| Quality | ruff + mypy + pre-commit |

## Reading guide

| Bạn muốn biết… | Đọc file |
|---|---|
| Stack + lý do chọn | [01-stack.md](01-stack.md) |
| Folder structure, layered design | [02-architecture.md](02-architecture.md) |
| BaseService, Repository, error handling | [03-patterns.md](03-patterns.md) |
| Pipeline flow từ RSS → Telegram | [04-pipeline.md](04-pipeline.md) |
| Config system, hot-reload | [05-config.md](05-config.md) |
| Test strategy, fixtures, mocking | [06-testing.md](06-testing.md) |

Cập nhật: 2026-09-04. Status: **DRAFT** (Phase 2 docs đang soạn, chưa implement).
