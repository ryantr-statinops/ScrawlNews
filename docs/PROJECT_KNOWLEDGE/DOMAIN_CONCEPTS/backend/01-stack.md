# 01 — Backend Stack

> Tech stack + lý do chọn cho backend (`src/`). Cập nhật 2026-09-04. Phase 2 docs DRAFT.

## Stack

| Layer | Library | Version | Lý do chọn |
|-------|---------|---------|------------|
| Runtime | Python | 3.11 | Stable, type hints tốt, performance |
| Web framework | FastAPI | 0.110+ | Async, auto OpenAPI, type-safe, Depends DI |
| ASGI server | Uvicorn | 0.29+ | Standard cho FastAPI |
| Task queue | Celery | 5.3+ | Beat schedule, retry, result backend, mature |
| Broker | Redis | 5.0+ | Đơn giản, hiệu quả, đã có sẵn |
| Database | SQLite | stdlib | Pure local, file-based, mount `./data` |
| DB access | sqlite3 | stdlib | Không cần ORM, raw SQL đủ cho personal tool |
| Validation | Pydantic | 2.0+ | Idiomatic FastAPI, type-safe |
| Settings | pydantic-settings | 2.0+ | Env loading, validation |
| Logging | structlog | 24.1+ | JSON output, context, dev/prod mode |
| Retry | tenacity | 8.2+ | Decorator-based, exponential backoff |
| HTTP client | httpx | 0.25+ | Async, dùng cho LLM/Telegram API |
| Rate limit | slowapi | 0.1.9+ | Per-IP, dùng FastAPI Limiter |
| Testing | pytest | 7.4+ | Standard Python testing |
| Async test | pytest-asyncio | 0.21+ | Test async code |
| Coverage | pytest-cov | 4.1+ | Track coverage |
| Lint | ruff | 0.4+ | Fast, thay thế flake8 + isort + black |
| Type | mypy | 1.10+ | Static type checking |
| Hooks | pre-commit | 3.6+ | Git hooks cho lint + typecheck |

## Quyết định chính (Phase 2 brainstorm)

### Database access: **sqlite3 thuần**

- ✅ Không cần ORM, ít learning curve
- ✅ Hiệu suất tốt cho SQLite (single-user, thousands of records)
- ✅ SQL trực tiếp, dễ debug bằng `sqlite3` CLI
- ❌ Không abstract → khó migrate sang PostgreSQL
- 📌 Lý do: Personal dashboard, SQLite đủ dùng. Nếu scale thì chuyển SQLAlchemy.

### DI: **FastAPI Depends**

- ✅ Idiomatic, type-safe
- ✅ Override dependency trong test dễ (`app.dependency_overrides`)
- ✅ Auto OpenAPI schema
- 📌 Settings inject qua `Depends(get_settings)`

### Error handling: **Custom exception classes → HTTP handlers**

- ✅ Service layer throw domain exception (không biết HTTP)
- ✅ Celery task cũng dùng được (không có HTTP context)
- ✅ Test dễ với `pytest.raises(ScrawlError)`
- ✅ Một chỗ map exception → HTTP status

```python
# Layered exception hierarchy
class ScrawlError(Exception): ...
class ScrawlerError(ScrawlError): ...
class SynthesizerError(ScrawlError): ...
class MessengerError(ScrawlError): ...
class NotFoundError(ScrawlError): ...
class ConfigError(ScrawlError): ...
```

### Logging: **structlog (JSON)**

- ✅ JSON output → dễ parse với log aggregator (Loki, Datadog)
- ✅ Context binding (request_id, run_id)
- ✅ Dev mode pretty-print, prod mode JSON
- ✅ Tích hợp stdlib logging
- 📌 Config trong `src/utils/logging.py`, gọi `configure_logging()` lúc startup

### Celery task: **1 task `pipeline.run` tổng**

- ✅ Đơn giản, dễ track
- ✅ Một chỗ retry nếu fail
- ✅ Phù hợp MVP
- 📌 Nếu cần fine-grained: tách thành 3 task (fetch/summarize/send) sau

### Retry: **3 retries, exponential backoff**

- ✅ Đủ cho network errors (timeout, 5xx)
- ✅ Exponential: 2s → 4s → 8s (tránh thundering herd)
- 📌 Per-service nếu cần (LLM có rate limit riêng, Telegram có RetryAfter)

### Request validation: **Pydantic models**

- ✅ Idiomatic FastAPI
- ✅ Type hints + auto OpenAPI schema
- ✅ Nested validation
- 📌 Dùng cho request body, query params, response model

### Auth: **Nginx HTTP Basic (opt-in)**

- ✅ Bảo vệ khi deploy public
- ✅ Không phụ thuộc app code
- ✅ Opt-in: tạo `.htpasswd` rồi mount, không có file = không có auth
- 📌 Web SPA public, chỉ `/api/*` cần password
- 📌 Tạo user: `htpasswd -c .htpasswd admin`

### API versioning: **No versioning, chỉ `/api/*`**

- ✅ MVP chưa cần versioning
- ✅ Khi cần thêm `/v2` prefix
- 📌 Breaking change → thêm version mới, giữ version cũ 1 tháng

### Cache: **No cache (FE TanStack Query đủ)**

- ✅ TanStack Query đã handle staleTime phía client
- ✅ Mỗi user (1 người) → ít traffic
- 📌 Nếu scale: thêm server cache cho `/api/stats` (60s TTL)

### Pub/Sub: **Polling + SSE (đang có)**

- ✅ SSE cho log streaming
- ✅ Polling 5s cho run status
- 📌 Mở rộng Redis pub/sub cho run events khi cần realtime updates

### Rate limit: **FastAPI slowapi (per-IP)**

- ✅ Per-IP, 60 req/min default
- ✅ 429 response khi vượt
- 📌 Per-endpoint: `Run Now` 1 lần/30s, config 1 lần/phút
- 📌 Nginx có thể thêm `limit_req` nếu public deploy

### Migration: **Script riêng chạy thủ công**

- ✅ `src/repositories/migrate.py` hiện tại
- ✅ Đơn giản, idempotent (CREATE TABLE IF NOT EXISTS)
- 📌 Auto-run on startup nếu muốn (sau)
- 📌 Alembic nếu cần track versioned migrations

### Background: **Celery + Beat (đang có)**

- ✅ Beat schedule, worker execute
- ✅ Result backend lưu task state
- 📌 GA cron vẫn là primary scheduler cho production

### Timezone: **UTC lưu, convert khi display**

- ✅ DB lưu UTC (standard)
- ✅ Display convert theo user timezone (Asia/Ho_Chi_Minh +7)
- 📌 FE nhận UTC, format local với `Intl.DateTimeFormat`

### File storage: **Local filesystem (data/)**

- ✅ Debug dễ, backup bằng `cp`
- ✅ Không cần S3 SDK
- 📌 Khi scale: MinIO hoặc S3-compatible

### Health check: **Liveness + Readiness**

- `/live` — process alive, no deps check (cho k8s liveness probe)
- `/ready` — DB + Redis check, 503 nếu fail (cho k8s readiness probe)
- `/health` — legacy, kept for backward compat

### OpenAPI docs: **FastAPI auto (Swagger UI)**

- ✅ `/docs` (Swagger UI) + `/redoc` (Redoc) tự động
- ✅ Không cần config
- 📌 Custom theme: tùy chỉnh CSS

## Status implement

| Item | Status |
|------|--------|
| FastAPI + Celery + Redis | ✅ Đã có |
| sqlite3 raw | ✅ Đã có |
| Pydantic 2 | ✅ Đã có |
| pydantic-settings | ✅ Đã có |
| tenacity | ✅ Đã có |
| httpx async | ✅ Đã có |
| structlog | ⏳ Planned |
| Custom exception classes | ⏳ Planned |
| Liveness + Readiness | ⏳ Planned |
| Nginx HTTP Basic | ⏳ Planned |
| FastAPI slowapi | ⏳ Planned |
| Test coverage 80%+ | 🔄 In progress |

## Tham khảo

- [02-architecture.md](02-architecture.md) — folder structure, layered design
- [03-patterns.md](03-patterns.md) — BaseService, Repository, error handling
- [04-pipeline.md](04-pipeline.md) — Celery pipeline flow
- [05-config.md](05-config.md) — config system, hot-reload
- [06-testing.md](06-testing.md) — pytest strategy
- [DECISIONS.md](../../DECISIONS.md) — ADR-011/012/013
