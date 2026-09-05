# Architecture Decision Records (ADR)

Ghi nhận các quyết định kiến trúc quan trọng đã chốt.

## ADR-001: Google News Data Source — RSS + trafilatura

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần lấy tin tức từ Google News. Google không cung cấp public API miễn phí.

### Options
1. **RSS Feed + trafilatura** — Google News có RSS feed công khai, trafilatura extract full content từ URL
2. **Playwright Scraping** — Crawl trực tiếp HTML, xử lý anti-bot, consent popup
3. **Third-party API** (SerpApi, NewsAPI, Tavily) — Trả phí, có rate limit

### Decision
Chọn **Option 1 (RSS + trafilatura)** làm primary.
**Fallback chain**: Nếu trafilatura fail → thử Readability-lxml → cuối cùng là Playwright (Option 2).

### Rationale
- RSS ổn định, không bị CAPTCHA, không cần browser
- trafilatura extract content tốt, xử lý được hầu hết news sites (F1=0.909)
- Readability-lxml làm fallback trung gian (F1=0.801), đơn giản, không cần network request phức tạp
- Playwright chỉ dùng khi cả hai thư viện trên fail (ví dụ: cấu trúc RSS thay đổi, site cần JS render)
- Chi phí = 0 (free)

### Consequences
- Không lấy được full content trực tiếp từ RSS (chỉ title + link + snippet)
- Cần request riêng từng URL để extract content → chậm hơn
- Phụ thuộc vào trafilatura maintainability

---

## ADR-002: LLM Provider — OpenRouter / OmniRoute (configurable)

**Date**: 2025-08-21
**Status**: Accepted
**Supersedes**: OpenAI gpt-4o-mini direct (now via OpenRouter/OmniRoute)

### Context
Cần LLM để tóm tắt tin tức. Cân bằng giữa chất lượng, chi phí, tốc độ. OpenAI gpt-4o-mini trả phí ($0.15/1K tokens).

### Options
| Option | Setup | Cost | Multi-model | Complexity |
|--------|-------|------|-------------|------------|
| **A: OpenRouter API** | Chỉ cần API key | Free - $0.15/1K | Manual switch | Thấp |
| **B: OmniRoute** | Cài Node.js + chạy server local | Free (auto route) | Auto-fallback | Trung bình |
| **C: Direct OpenAI** | API key trực tiếp | $0.15/1K | Manual switch | Thấp |

### Decision
- **Phase 1**: Dùng **OpenRouter API** làm default — đơn giản, không cần server.
- **Phase 2+**: Có thể chuyển sang **OmniRoute** nếu cần auto-fallback giữa nhiều providers.
- Giữ `LLM_API_KEY` env var để backward compatible với OpenAI direct.
- Thêm `OPENROUTER_API_KEY` cho OpenRouter/OmniRoute.

### Rationale
- OpenRouter có nhiều free models (`google/gemma-2-9b-it`, `meta/llama-3-8b-instruct`)
- OmniRoute cung cấp auto-fallback + RTK token compression (tiết kiệm 20-40% tokens)
- Chi phí giảm đáng kể so với direct OpenAI
- Dễ switch provider qua `LLM_PROVIDER` env var

### Consequences
- Cần quản lý 2 API keys (`LLM_API_KEY` + `OPENROUTER_API_KEY`)
- Config phải support switch provider qua `LLM_PROVIDER` env var
- OmniRoute cần Node.js runtime trên GitHub Actions runner
- Chi phí batch 20 articles: ~$0.0001-0.0002 (OpenRouter) so với ~$0.001 (OpenAI direct)

---

## ADR-003: Storage — SQLite

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần lưu articles, summaries để dedup, history, re-summarize.

### Options
1. **SQLite** — File-based, zero-config, đủ cho single-user
2. **PostgreSQL** — Production-grade, cần server
3. **JSON files** — Simple, nhưng query khó
4. **In-memory** — Mất data khi restart

### Decision
Chọn **SQLite** với schema: `articles` + `summaries` tables.

### Rationale
- Zero setup, phù hợp GitHub Actions runner
- ACID, query linh hoạt
- Dễ backup (chỉ copy file)
- Đủ cho personal use (thousands of records)

---

## ADR-004: Orchestration — Single Python Script

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần chạy pipeline: fetch → summarize → send.

### Options
1. **Single script (`main.py`)** — Simple, trực quan
2. **Workflow engine** (Airflow, Prefect, Dagster) — Overkill
3. **Makefile + shell** — Khó debug, error handling yếu

### Decision
Chọn **single async Python script** (`src/main.py`) với class `Pipeline`.

### Rationale
- Dễ hiểu, dễ debug, dễ test
- Async I/O hiệu quả cho network calls
- Không cần dependency ngoài stdlib + requirements
- GitHub Actions chạy được trực tiếp

---

## ADR-005: Deployment — GitHub Actions

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần chạy tự động 4 lần/ngày.

### Options
1. **GitHub Actions** — Free, integrated, cron support
2. **VPS + cron** — Tốn tiền, maintain server
3. **AWS Lambda / Cloud Functions** — Setup phức tạp
4. **Render / Fly.io** — Có free tier nhưng giới hạn

### Decision
Chọn **GitHub Actions** với cron `0 8,12,16,21 * * *`.

### Rationale
- Free cho public repo, 2000 min/tháng cho private
- Secrets management built-in
- Logs, artifacts, re-run UI
- Playwright chạy được trên ubuntu-latest runner

---

## ADR-006: Language — Vietnamese Output

**Date**: 2025-08-21
**Status**: Accepted

### Context
Newsletter gửi về Telegram, ngôn ngữ nào?

### Decision
**Tiếng Việt** cho newsletter content. Code/comments/docs bằng tiếng Anh (chuẩn dev).

### Rationale
- User là tiếng Việt
- LLM hỗ trợ tốt tiếng Việt
- Code tiếng Anh dễ maintain, share, hire

---

## ADR-007: Deduplication — URL SHA256 Hash

**Date**: 2025-08-21
**Status**: Accepted

### Context
Tránh gửi trùng tin tức đã fetch trước đó.

### Decision
Dùng `SHA256(url)[:16]` làm `article_id` (primary key).

### Rationale
- Deterministic: cùng URL → cùng ID
- Không cần central ID generator
- 16 hex chars = 64 bits → collision probability gần 0
- Simple, no external deps

---

## ADR-008: Error Handling — Graceful Degradation

**Date**: 2025-08-21
**Status**: Accepted

### Context
Pipeline không được "chết" khi một component fail.

### Decision
| Component fail | Fallback |
|---------------|----------|
| Scrawler | Log error, exit (nothing to process) |
| Synthesizer (LLM) | Gửi raw article titles + URLs |
| Messenger (Telegram) | Save to local file, retry next run |
| Individual article extract | Skip article, continue others |

### Rationale
- Partial success > total failure
- User vẫn nhận được thông tin (raw titles) khi LLM fail
- Telegram fail không làm mất data (có local backup)

---

## ADR-009: LLM Provider — OpenRouter / OmniRoute Options

**Date**: 2025-08-22
**Status**: Accepted

### Context
Cần LLM để tóm tắt tin tức. OpenAI gpt-4o-mini trả phí ($0.15/1K tokens). Có nhiều free/cheaper alternatives.

### Options
| Option | Setup | Cost | Multi-model | Complexity |
|--------|-------|------|-------------|------------|
| **A: OpenRouter API** | Chỉ cần API key | Free - $0.15/1K | Manual switch | Thấp |
| **B: OmniRoute** | Cài Node.js + chạy server local/VPS | Free (auto route) | Auto-fallback | Trung bình |
| **C: Direct OpenAI** | API key trực tiếp | $0.15/1K | Manual switch | Thấp |

### Decision
- **Phase 1**: Dùng **Option A (OpenRouter)** làm default — đơn giản, không cần server.
- **Phase 2+**: Có thể chuyển sang **Option B (OmniRoute)** nếu cần auto-fallback giữa nhiều providers.

### Rationale
- OpenRouter có nhiều free models (`google/gemma-2-9b-it`, `meta/llama-3-8b-instruct`)
- OmniRoute cung cấp auto-fallback + RTK token compression (tiết kiệm 20-40% tokens) + OpenTelemetry + cost tracking
- Giữ `LLM_API_KEY` env var để backward compatible với OpenAI direct
- Thêm `OPENROUTER_API_KEY` cho OpenRouter/OmniRoute

### Consequences
- Cần quản lý 2 API keys (`LLM_API_KEY` + `OPENROUTER_API_KEY`)
- Config phải support switch provider qua `LLM_PROVIDER` env var
- OmniRoute cần Node.js runtime trên GitHub Actions runner
- Chi phí batch 20 articles: ~$0.0001-0.0002 (OpenRouter) so với ~$0.001 (OpenAI direct)

---

## ADR-010: Hosting & Database Strategy

**Date**: 2025-08-24
**Status**: Accepted

### Context
ScrawlNews cần:
1. OmniRoute instance riêng, không dùng chung máy local
2. Database lưu articles/summaries, không cần dung lượng lớn
3. Chi phí $0/tháng (free tier)

### Options

| Component | Option | Free tier | Pros | Cons |
|-----------|--------|-----------|------|------|
| **OmniRoute host** | Fly.io | 3 shared VMs, 256MB RAM | Free, ổn định, Docker support | Giới hạn RAM |
| | Render | Free web service, 512MB RAM | Đơn giản, dashboard | Spin-down sau 15min |
| | Railway | Không còn free | - | $5/tháng |
| **Database** | SQLite local | Free | Zero-config, đủ cho personal | Không remote access |
| | Turso | 5GB free | SQLite edge DB, replication | Mới, cần learning curve |
| | Neon | 0.5GB free | PostgreSQL, serverless | Hơi nhỏ |
| | Supabase | 500MB free | PostgreSQL, BaaS | Không dùng trong dự án |

### Decision
- **OmniRoute**: Fly.io free tier (3 shared VMs, 256MB RAM)
- **Database**: SQLite local cho Phase 1, Turso cho Phase 2+ nếu cần remote
- **Pipeline**: GitHub Actions cron (free)
- **Total cost**: $0/tháng

### Rationale
- Fly.io có free tier đủ cho OmniRoute (256MB RAM, 160MB disk)
- SQLite local đủ cho personal use, Turso free 5GB nếu cần remote
- GitHub Actions đã có sẵn, không cần hosting pipeline
- Tổng chi phí $0/tháng phù hợp với mục tiêu personal project

### Consequences
- OmniRoute instance trên Fly.io phải restart nếu exceed 256MB RAM
- SQLite local không remote access → cần Turso nếu muốn access từ nhiều máy
- Cần backup SQLite định kỳ nếu dùng local
- Fly.io cần credit card để verify account (không trừ tiền)

---

## ADR-011: Dashboard-First — Local Monitor Dashboard as Primary Service

**Date**: 2026-08-27
**Status**: Accepted
**Supersedes**: ADR-004 (Single Python Script) extended, ADR-005 (Deployment only GA) extended

### Context
Ban đầu newsbot (fetch → summarize → Telegram) là service chính. Nhu cầu mới: service chính là **local dev hosting monitor dashboard** bật bằng 1 terminal, newsbot chỉ là 1 feature toggle trong dashboard. Dashboard cần full 6 nhóm: Feed Monitor, Summarization Monitor, Pipeline Control, Delivery Monitor, System/Health, Analytics.

### Options
| Option | Stack | Pipeline scheduler | Gateway | Complexity |
|--------|-------|-------------------|---------|------------|
| **A: FastAPI + Celery + Redis + React Vite + Nginx** | Python trọng tâm, Nginx đơn giản | Giữ GitHub Actions cron + Celery Beat local | Nginx | Trung bình |
| B: FastAPI + APScheduler + Traefik | Không cần Redis | Chỉ GA, APScheduler in-process | Traefik (Go) | Thấp |
| C: Go micro-service + FastAPI | Go fetcher sidecar | GA + Go worker | Traefik | Cao |

### Decision
Chọn **Option A** theo yêu cầu user:
- **Backend**: FastAPI + Celery + Redis (broker + result backend), giữ toàn bộ `Scrawler/Synthesizer/Messenger` Python (Pydantic Settings mở rộng `redis_url`, `celery_broker_url`, `telegram_enabled` toggle).
- **Frontend**: React 18 + TypeScript + Vite + Mantine UI v7 + TanStack Router + TanStack Query + ApexCharts + Zustand + SSE (`web/`). Xem [DOMAIN_CONCEPTS/frontend/01-stack.md](DOMAIN_CONCEPTS/frontend/01-stack.md) để biết chi tiết.
- **Gateway**: Nginx (thay Traefik cho đơn giản, Go-base infra không cần Go service).
- **Scheduler**: Giữ GitHub Actions cron `0 8,12,16,21 * * * UTC` làm primary, Celery Beat chỉ cho local manual trigger / dev schedule. Newsbot là feature `telegram_enabled` on/off.
- **Dev DX**: Hỗ trợ cả `docker compose up` (api + worker + beat + redis + web + nginx) và `make dev` (concurrently uvicorn + celery + vite).

### Rationale
- Celery + Redis cho task async, retry 3x, poll `task_id`, Beat schedule — cần cho Pipeline Control (Run Now, history, retry) và 6 feature dashboard; APScheduler in-process sẽ chết khi uvicorn restart.
- Nginx đơn giản, config `nginx.conf` route `/api → :8000`, `/ → :5173`, không cần Go runtime như Traefik.
- React Vite là yêu cầu khóa, Mantine UI cung cấp đầy đủ component (Table, Form, Notifications, AppShell) cho dashboard monitor.
- Giữ GA giảm chi phí local, dashboard chỉ monitor + trigger.

### Consequences
- Thêm Redis (~25MB) và 2 container `worker`/`beat`; `requirements.txt` thêm `celery[redis]>=5.3`, `redis>=5.0`.
- `docker-compose.yml` + `nginx.conf` mới, `Makefile` thêm `make dev`, `make worker`, `make beat`.
- `spec/api.yaml:1` mở rộng 10+ endpoints `/api/articles`, `/summaries`, `/runs`, `/config`, `/tasks/{id}`, `/logs/stream`.
- SQLite vẫn Phase 1, nhưng `database_url` phải configurable cho volume mount.
- Cần ADR-012 sau nếu quyết định tách Go fetcher sidecar.

> **Update 2026-09-03**: Frontend stack thay đổi. Bỏ shadcn/Tailwind/Recharts, thêm Mantine UI v7 + TanStack Router + Zustand + ApexCharts. Xem [DOMAIN_CONCEPTS/frontend/01-stack.md](DOMAIN_CONCEPTS/frontend/01-stack.md).

---

## ADR-012: Task Queue — Celery + Redis (vs APScheduler / RQ)

**Date**: 2026-08-27
**Status**: Accepted

### Context
Cần queue cho `pipeline.run` khi dashboard bấm Run Now và cho Beat schedule. Trước đó dùng `tenacity` retry in-process.

### Options
1. **Celery + Redis** — distributed, retry, result backend, Beat
2. **APScheduler** — in-process, zero deps, mất job khi restart
3. **RQ (Redis Queue)** — đơn giản hơn Celery nhưng thiếu Beat

### Decision
Chọn **Celery + Redis**. `redis_url` default `redis://localhost:6379/0` local, `redis://redis:6379/0` trong docker. Broker = Redis DB 0, result = DB 1.

### Rationale
- Cần cho 6 feature: Pipeline Control (task poll), Delivery Monitor (retry), Analytics (result store).
- Beat thay cron local khi dev không dùng GA.
- RQ thiếu Beat, APScheduler không persist.

### Consequences
- Thêm `celery` và `redis` deps, `src/worker/celery_app.py` + `src/worker/tasks.py`.
- Local dev phải chạy `redis-server` (docker hoặc native).
- `make dev` phải spawn `celery -A src.worker.celery_app worker --loglevel=info` song song với uvicorn.

---

## ADR-013: Config Persistence, Migration and Web Lint Flat

**Date**: 2026-08-28
**Status**: Accepted

### Context
Stage 3 cần persist `PUT /api/config` 4 vars hot-reload + audit history, và web lint flat config `eslint.config.js` thay `--ext`.

### Options
1. **Config in DB + Redis pub/sub** — `settings` + `config_history` tables, `ConfigRepository` với `run_migrations`, `GET /api/config/history`
2. **Config in memory only** — mất sau restart
3. **Web lint flat** — `eslint.config.js` với `eslint-plugin-react` etc, thay `eslint src --ext`

### Decision
Chọn **Option 1 + 3**: Thêm `src/repositories/config_repo.py` + `migrate.py` v2 `settings`/`config_history` + `GET /api/config/history` + Redis `scrawlnews:config` publish (`src/api/routes/config.py:11`); web `eslint src` flat với plugins `eslint-plugin-react` etc (`web/package.json:12`).

### Rationale
- Persist survive restart, audit cho hot-reload, temp_db isolation cho tests (`tests/unit/test_config.py:1` isolation)
- Flat config là chuẩn ESLint 8+, `--ext` deprecated

### Consequences
- `src/repositories/migrate.py` SCHEMA_VERSION 2, `ConfigRepository` tạo bảng nếu thiếu
- `make lint` đổi `web` sang `npm run lint` flat, thêm deps `@eslint/js`, `globals`