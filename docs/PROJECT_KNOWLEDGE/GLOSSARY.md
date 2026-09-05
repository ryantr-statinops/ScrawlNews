# Glossary

> Bảng chú giải thuật ngữ dùng trong ScrawlNews docs. Cập nhật 2026-09-04.

## Reading guide

- Mỗi thuật ngữ 1-2 dòng, kèm link tới docs chi tiết (nếu có)
- Tra cứu nhanh khi đọc docs khác mà gặp thuật ngữ lạ
- Dùng Ctrl+F để tìm nhanh

---

## Pipeline

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **RSS** | XML feed format, Google News cung cấp `news.google.com/rss/search?q=...` |
| **feedparser** | Python lib parse RSS/Atom feeds, dùng trong Scrawler |
| **Trafilatura** | Python lib extract main text từ HTML, F1=0.909 (best) |
| **Readability-lxml** | Python port của Mozilla Readability, F1=0.801 (fallback) |
| **Playwright** | Headless browser, dùng cuối cùng khi các extractor fail |
| **Scrawler** | Service fetch articles từ RSS + extract content (Stage 1) |
| **Synthesizer** | Service summarize articles bằng LLM (Stage 2) |
| **Messenger** | Service gửi summaries qua Telegram, feature toggle `telegram_enabled` |
| **Newsletter** | Output của Messenger, danh sách summaries formatted Markdown |
| **dedup / deduplication** | Loại bỏ trùng lặp, dùng `SHA256(url)[:16]` làm article_id |
| **fallback** | Hành vi khi primary fail: dùng cách khác (e.g., raw titles nếu LLM fail) |

## Async / Task Queue

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **Celery** | Distributed task queue Python, dùng Redis làm broker |
| **Beat** | Celery scheduler, chạy task theo cron (e.g., mỗi 30 phút) |
| **Worker** | Celery process execute task |
| **Broker** | Message queue giữa producer (FastAPI) và consumer (worker) |
| **Result backend** | Lưu kết quả task, ScrawlNews dùng Redis DB 1 |
| **pipeline.run** | Tên Celery task tổng, chạy Scrawler → Synthesizer → Messenger |
| **task_id** | UUID Celery assign cho mỗi task, dùng poll status |
| **max_retries** | Số lần retry tối đa (default 3 với exponential backoff) |
| **exponential backoff** | Retry delay tăng theo cấp số nhân: 2s → 4s → 8s |
| **tenacity** | Python lib retry với decorator, dùng trong services |
| **Redis** | In-memory key-value store, làm Celery broker + result backend |
| **Redis pub/sub** | Pattern publish/subscribe, ScrawlNews dùng cho config hot-reload |
| **SSE** | Server-Sent Events, push realtime 1 chiều qua HTTP |
| **polling** | Client gọi API định kỳ (e.g., mỗi 5s) thay vì SSE |

## LLM

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **LLM** | Large Language Model, dùng để summarize articles |
| **OpenAI** | Provider LLM trả phí (gpt-4o-mini, gpt-4o) |
| **OpenRouter** | API gateway cho nhiều LLM providers, có nhiều free models |
| **OmniRoute** | Self-hosted LLM router, auto-fallback giữa providers |
| **RTK** | Routing Token Kit, OmniRoute dùng giảm 20-40% tokens |
| **prompt** | Input text gửi tới LLM, gồm system + user message |
| **batch** | Gộp nhiều articles vào 1 prompt để tiết kiệm tokens |
| **token** | Đơn vị LLM đọc, ~4 chars English, ~1-2 chars tiếng Việt |
| **fallback** | Khi LLM fail, dùng raw titles + URLs |
| **temperature** | LLM randomness, 0=deterministic, 1=creative |
| **max_tokens** | Giới hạn output length, default 800 trong Synthesizer |
| **model_used** | Field trong `summaries` table, lưu model đã dùng (e.g., `gpt-4o-mini`, `raw_fallback`) |

## Web / API

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **FastAPI** | Python web framework async, auto OpenAPI schema |
| **Uvicorn** | ASGI server chạy FastAPI |
| **Nginx** | Reverse proxy, route `/api → :8000`, `/ → :5173` |
| **Pydantic** | Python lib data validation + serialization |
| **Depends** | FastAPI dependency injection mechanism |
| **OpenAPI** | API spec format (Swagger), FastAPI tự gen |
| **Swagger UI** | Web UI cho OpenAPI docs, ở `/docs` |
| **CORS** | Cross-Origin Resource Sharing, header cho cross-domain |
| **SSE** | Server-Sent Events, content-type `text/event-stream` |
| **polling** | Client gọi API định kỳ (e.g., 5s) |
| **TanStack Query** | React lib cho server state, cache, refetch |
| **Mantine** | React UI library v7, có sẵn theme + components |
| **ApexCharts** | Chart library, support realtime update via `updateSeries` |
| **Zustand** | Lightweight state management cho React |
| **TanStack Router** | Type-safe router cho React |

## Storage

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **SQLite** | File-based SQL database, ScrawlNews dùng (no server) |
| **sqlite3** | Python stdlib module, dùng raw SQL (no ORM) |
| **WAL** | Write-Ahead Logging, SQLite mode cho concurrency tốt hơn |
| **schema** | Cấu trúc tables + columns, định nghĩa trong `migrate.py` |
| **migration** | Script update schema, idempotent (CREATE TABLE IF NOT EXISTS) |
| **INDEX** | Cấu trúc tăng tốc query, khai báo trong schema |
| **FK (Foreign Key)** | Constraint tham chiếu giữa tables |
| **INSERT OR IGNORE** | SQLite SQL, skip nếu duplicate, dùng cho dedup |
| **RETURNING** | SQLite SQL extension, trả về row vừa insert |
| **datetime('now', '-N days')** | SQLite datetime function, dùng cho retention cleanup |
| **VACUUM** | SQLite command rebuild DB file, giảm size |
| **PRAGMA** | SQLite config commands (e.g., `PRAGMA journal_mode=WAL`) |

## Architecture / Pattern

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **ADR** | Architecture Decision Record, ghi lại quyết định kỹ thuật |
| **BaseService** | Abstract class trong `src/services/base.py`, có method `execute()` |
| **Repository Pattern** | Layer truy cập DB, abstract CRUD qua class methods |
| **Layered Architecture** | API → Service → Repository → Model, mỗi layer 1 trách nhiệm |
| **DI / Dependency Injection** | Inject dependencies qua constructor hoặc FastAPI Depends |
| **Service Locator** | Pattern global singleton, ScrawlNews KHÔNG dùng |
| **DTO** | Data Transfer Object, Pydantic model truyền giữa layers |
| **Hot-reload** | Đổi config không cần restart, ScrawlNews support 4 vars |
| **Idempotent** | Operation có thể chạy nhiều lần, kết quả giống nhau |
| **Graceful degradation** | Partial success > total failure, log + continue |

## Telegram

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **Telegram Bot** | Bot API, dùng `python-telegram-bot` lib |
| **chat_id** | ID chat/channel để gửi message, public info |
| **bot_token** | Token authenticate bot, **SECRET** |
| **RetryAfter** | Exception khi Telegram rate limit, có `retry_after` seconds |
| **Markdown** | Telegram parse mode, bold, italic, code, link |
| **MarkdownV2** | Version mới hơn, escape nhiều hơn |
| **inline keyboard** | Button dưới message, click để trigger action |

## ScrawlNews specific

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **ScrawlError** | Base exception class trong `src/services/exceptions.py` |
| **ScrawlerError** | Exception cho Scrawler failures |
| **SynthesizerError** | Exception cho LLM failures |
| **MessengerError** | Exception cho Telegram failures |
| **NotFoundError** | Exception khi entity không tồn tại trong DB |
| **ConfigError** | Exception cho config validation failures |
| **fetch_limit** | Env var `FETCH_LIMIT`, max articles per run (default 20) |
| **summary_lang** | Env var `SUMMARY_LANG`, output language (default `vi`) |
| **retention_days** | Env var `RETENTION_DAYS`, data TTL (default 7) |
| **telegram_enabled** | Env var `TELEGRAM_ENABLED`, toggle Messenger service |
| **PipelineRun** | DB table track mỗi pipeline execution |
| **stage** | 1 trong 3: Scrawler / Synthesizer / Messenger |
| **dashboard-first** | ADR-011: Dashboard là primary service, newsbot là feature |
| **GA cron** | GitHub Actions cron `0 8,12,16,21 * * *`, primary scheduler |
| **Nginx parity** | `make dev` cũng chạy Nginx Docker để giống prod |

## Testing

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **pytest** | Python test framework |
| **pytest-asyncio** | Plugin test async code |
| **pytest-cov** | Coverage report |
| **mock / AsyncMock** | Replace function/class với fake, control return value |
| **fixture** | Reusable test setup, định nghĩa trong `conftest.py` |
| **TestClient** | FastAPI test client, gọi endpoint không cần server |
| **temp_db** | Temporary SQLite file cho test, auto cleanup |
| **coverage** | % code được test, target 85% |
| **patch** | Monkey-patch function trong test |
| **side_effect** | Mock raise exception hoặc return multiple values |

## DevOps

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **docker-compose** | Multi-container Docker config, ScrawlNews có 6 services |
| **Nginx** | Reverse proxy, public entrypoint |
| **GitHub Actions** | CI/CD free cho public repo |
| **cron** | Schedule syntax, `0 8,12,16,21 * * *` = 4 lần/ngày UTC |
| **pre-commit** | Git hook chạy lint/typecheck trước khi commit |
| **ruff** | Fast Python linter (thay flake8 + isort + black) |
| **mypy** | Static type checker cho Python |
| **.env** | File chứa env vars, gitignored |
| **.env.example** | Template, committed |
| **secret** | Sensitive value (token, key), không commit |
| **Secrets (GitHub)** | Encrypted env vars trong repo settings |

## Performance

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **throughput** | Số operations per second, ScrawlNews thấp (personal use) |
| **latency** | Thời gian từ request → response, ~30-60s per run |
| **retry-after** | HTTP header hoặc Telegram field, sleep trước khi retry |
| **circuit breaker** | Pattern chống cascade failure, chưa implement (TODO) |
| **rate limit** | Giới hạn requests/time, dùng slowapi |
| **TTL** | Time-to-live, dùng cho retention_days |
| **bottleneck** | Stage chậm nhất, thường là LLM call |

## References

- [docs/PROJECT_KNOWLEDGE/DECISIONS.md](DECISIONS.md) — ADRs
- [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/backend/](DOMAIN_CONCEPTS/backend/) — backend docs
- [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/](DOMAIN_CONCEPTS/frontend/) — frontend docs
- [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/pipeline/](DOMAIN_CONCEPTS/pipeline/) — pipeline docs
