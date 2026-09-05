# Documentation Roadmap

> Kế hoạch tổng thể cho việc soạn docs dự án ScrawlNews. Lưu lại tiến độ, phần đã xong, phần đang làm, phần sẽ làm tiếp.
> Cập nhật: 2026-09-04

## Mục đích

- Track tiến độ soạn docs
- Liệt kê phần đã hoàn thành với commit hash
- Liệt kê phần đang thực hiện
- Liệt kê phần sẽ làm tiếp theo với thứ tự ưu tiên
- Lưu lại context cho AI agent hoặc contributor tương lai

## Quy tắc

- Mỗi phần lớn tạo 1 PR / chuỗi commit nhỏ (theo AGENTS.md)
- Không sửa source code trong khi soạn docs
- Mỗi file docs mới: tạo commit riêng, push ngay
- Update file này sau mỗi commit hoàn thành
- Ưu tiên: cấu trúc dễ đọc > cấu trúc dễ navigate > cấu trúc dễ maintain

---

## Trạng thái

| Giai đoạn | Trạng thái |
|-----------|------------|
| Restructure `docs/` (PROJECT_KNOWLEDGE / EXECUTION / GUIDES) | ✅ Done |
| Cleanup dead refs + rà soát | ✅ Done |
| Soạn `frontend/` (stack, design tokens, architecture, patterns) | ✅ Done |
| Soạn `backend/` (stack, architecture, patterns, pipeline, config, testing) | ✅ Done |
| Soạn `pipeline/` (overview, sequence, data-model, performance) | ✅ Done |
| Soạn glossary | ✅ Done |
| Soạn `frontend/05-testing.md` (Vitest + RTL) | ✅ Done |
| Soạn FAQ + QUICKSTART + README polish | ✅ Done |

---

## Phase 0: Restructure + Cleanup (DONE)

### Restructure (commits `78d88b6`..`13f15b8`, ngày 2026-08-31)

Tạo cấu trúc mới:
```
docs/
├── README.md
├── PROJECT_KNOWLEDGE/   # knowledge: là gì, tại sao
├── EXECUTION/            # action: làm gì, đã làm gì
└── GUIDES/               # how-to: setup, test, deploy
```

20 commits, mỗi file 1 commit.

### Cleanup & sync (commits `c3fe5b2`..`a1dbca2`, ngày 2026-09-03)

- Thêm `celerybeat-schedule` vào `.gitignore`
- Sửa stale refs trong `.agent/SKILL/`
- Fix 4 stale refs trong `DECISIONS.md` (ADR-011/012)
- Sync `api.yaml` với code (xóa 3 endpoints unimplemented)
- Sync env table `setup.md` với `.env.example` (thêm `APP_ENV`)
- Rename "Skill" → "Service" trong `01-overview.md` + `changelog.md`

---

## Phase 1: Frontend Stack Docs (DONE)

### Commits

| Commit | Nội dung |
|--------|----------|
| `b630bf3` | docs: add DOMAIN_CONCEPTS/frontend (5 files) |
| `dd4ab93` | docs: simplify 03-interface Web section |
| `eb23661` | docs: update ADR-011 frontend stack |
| `e97f720` | docs: update README stack table |

### Files tạo mới

```
docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/
├── README.md            # Index + reading guide
├── 01-stack.md          # Mantine + ApexCharts + TanStack Router + Zustand
├── 02-design-tokens.md  # Color, Inter + JetBrains Mono, spacing
├── 03-architecture.md   # Folder structure, routing, state rules
└── 04-patterns.md       # SSE, error, loading, form, chart, notification
```

### Quyết định đã chốt

- React 18 + TypeScript + Vite
- Routing: **TanStack Router** (thay React Router)
- UI: **Mantine UI v7** (bỏ shadcn/Tailwind)
- Chart: **ApexCharts** (bỏ Recharts)
- State: **Zustand** (global UI) + TanStack Query (server)
- Realtime: SSE (`EventSource`)
- Form: Mantine form + Zod
- Icon: Lucide React
- Color palette: Primary `#2563EB`/`#60A5FA`, Accent `#00C7FC`
- Font: Inter + JetBrains Mono
- Theme: Light + Dark toggle (Zustand persist localStorage)

### Đã cập nhật cross-refs

- `03-interface.md`: rút gọn phần Web, ref sang `frontend/`
- `DECISIONS.md` ADR-011: update frontend stack + note 2026-09-03
- `README.md`: update bảng Stack row Dashboard Frontend

---

## Phase 2: Backend Stack Docs (DONE)

### Mục tiêu

Tạo `DOMAIN_CONCEPTS/backend/` tương tự `frontend/`, document chi tiết backend stack.

### Files đã tạo (commits `841fd95`..`625e0f2`)

```
docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/backend/
├── README.md            # Index + reading guide
├── 01-stack.md          # 18 quyết định Phase 2 (sqlite3, Depends, custom exc, structlog, ...)
├── 02-architecture.md   # Layered: api → services → repos → models
├── 03-patterns.md       # BaseService, Repository, error handling, retry, logging
├── 04-pipeline.md       # Celery pipeline.run flow + data flow + edge cases
├── 05-config.md         # Pydantic Settings, hot-reload, secrets
└── 06-testing.md        # Pytest fixtures, mocking, coverage
```

### 18 quyết định đã chốt

1. DB access: sqlite3 thuần
2. DI: FastAPI Depends
3. Error: Custom exception classes
4. Logging: structlog (JSON)
5. Task: 1 task pipeline.run tổng
6. Retry: 3 retries, exponential backoff
7. Validation: Pydantic models
8. Auth: Nginx HTTP Basic
9. Versioning: No versioning
10. Cache: No cache (FE TanStack đủ)
11. Pub/Sub: Polling + SSE
12. Rate limit: FastAPI slowapi
13. Migration: Script riêng
14. Background: Celery + Beat
15. Timezone: UTC lưu, convert display
16. File storage: Local filesystem
17. Health: Liveness + Readiness
18. OpenAPI: FastAPI auto (Swagger UI)

### Implement status

| Item | Status |
|------|--------|
| FastAPI + Celery + Redis | ✅ Đã có |
| sqlite3 raw | ✅ Đã có |
| Pydantic 2 | ✅ Đã có |
| structlog | ⏳ Planned (Phase 3+) |
| Custom exception classes | ⏳ Planned (Phase 3+) |
| Liveness + Readiness | ⏳ Planned (Phase 3+) |
| Nginx HTTP Basic | ⏳ Planned (Phase 3+) |
| FastAPI slowapi | ⏳ Planned (Phase 3+) |

### Câu hỏi cần trả lời trước khi soạn

- [ ] Có dùng SQLAlchemy ORM hay chỉ sqlite3 raw? (hiện code dùng sqlite3 trực tiếp)
- [ ] DI pattern: FastAPI Depends? Service locator? Hay không dùng DI?
- [ ] Error handling: custom exception classes? HTTPException trực tiếp? Middleware?
- [ ] Logging: structlog? stdlib logging? JSON format?
- [ ] Celery task structure: 1 task lớn `pipeline.run` hay nhiều task nhỏ?
- [ ] Repository pattern: instance methods hay class methods?

### Nội dung mỗi file (dự kiến)

**01-stack.md**
- Python 3.11
- FastAPI 0.110
- Celery 5.3 + Redis 5.0
- SQLAlchemy 2 (hoặc sqlite3 thuần)
- Pydantic 2 + pydantic-settings
- pytest 7 + pytest-asyncio + pytest-cov
- ruff + mypy
- tenacity (retry)

**02-architecture.md**
- Folder structure `src/`
- Layer responsibilities (api, services, repositories, models)
- Request flow: HTTP → API route → service → repository → DB
- Background task flow: HTTP → Celery task → service → DB

**03-patterns.md**
- BaseService abstract class
- Repository pattern (CRUD + dedup)
- Config injection (Pydantic Settings)
- Error handling per layer
- Retry with tenacity
- Logging conventions

**04-pipeline.md**
- Pipeline.run flow
- Stage-by-stage detail: Scrawler → Synthesizer → Messenger
- Data flow: RSS → Article → Summary → Telegram
- Error handling per stage
- Idempotency / dedup
- PipelineRun tracking

**05-config.md**
- Pydantic Settings structure
- Env var categories: secrets, connection, runtime
- Hot-reload: limited 4 vars
- Validation: telegram_enabled requires token
- env override: localhost vs docker

**06-testing.md**
- Test structure: unit, integration
- Conftest fixtures
- Mocking: httpx, openai, telegram
- temp_db isolation
- ConfigRepository temp_db
- Coverage targets

### Cập nhật cross-refs sau Phase 2

- `02-core-engine.md`: tham chiếu `backend/01-stack.md` thay vì liệt kê trực tiếp
- `04-data-config.md`: tham chiếu `backend/05-config.md`
- `TARGET_ARCHITECTURE.md`: cập nhật diagram nếu cần
- `DECISIONS.md` ADR-011/012: thêm note ref đến `backend/`

---

## Phase 3: Pipeline & Data Flow (DONE)

### Mục tiêu

Document chi tiết luồng data từ RSS → Telegram, vẽ diagram rõ ràng, document retry + error handling per stage.

### Files đã tạo (commits `91e21d6`..`b951adf`)

```
docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/pipeline/
├── README.md
├── 01-overview.md       # Stages, error flow, retry
├── 02-sequence.md       # Mermaid sequence diagrams
├── 03-data-model.md     # ER diagram, tables, lifecycle
└── 04-performance.md    # Dashboard metrics, cost, scaling
```

### Diagrams (Mermaid)

- **Sequence**: happy path, error path (Scraper retry), LLM fallback, dashboard polling, trigger sources
- **ER**: articles ↔ summaries ↔ pipeline_runs ↔ settings ↔ config_history
- **Performance visual**: timing breakdown, cost breakdown, scaling considerations

### Bỏ qua (đơn giản hóa cho MVP)

- State machine diagram cho PipelineRun lifecycle (chỉ table)
- Flowchart decision/retry (chỉ error flow ASCII)
- Prometheus metrics (chưa cần cho MVP)

---

## Phase 4: Glossary (DONE)

### Mục tiêu

Tra cứu nhanh các thuật ngữ dùng trong docs, hỗ trợ onboarding.

### File đã tạo (commit `49bdf89`)

`docs/PROJECT_KNOWLEDGE/GLOSSARY.md` — 197 dòng, ~100 thuật ngữ.

### Categories

| Category | Số thuật ngữ |
|----------|--------------|
| Pipeline (Scrawler, Synthesizer, Messenger, ...) | 11 |
| Async / Task Queue (Celery, Beat, Redis, SSE, ...) | 14 |
| LLM (OpenRouter, OpenAI, tokens, prompt, ...) | 12 |
| Web / API (FastAPI, Mantine, ApexCharts, ...) | 14 |
| Storage (SQLite, schema, migration, ...) | 12 |
| Architecture / Pattern (ADR, BaseService, Repository, ...) | 10 |
| Telegram (Bot, chat_id, Markdown, ...) | 7 |
| ScrawlNews specific (ScrawlError, PipelineRun, ...) | 15 |
| Testing (pytest, mock, fixture, ...) | 10 |
| DevOps (docker, GitHub Actions, ruff, ...) | 11 |
| Performance (throughput, latency, ...) | 7 |
| **Tổng** | **~123** |

---

## Phase 5: Testing Docs (DONE)

### Mục tiêu

Tách testing strategy thành docs riêng cho BE và FE.

### Files

| File | Status | Commit |
|------|--------|--------|
| `docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/backend/06-testing.md` | ✅ (Phase 2) | `625e0f2` |
| `docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/05-testing.md` | ✅ (Phase 5) | `6ae34c5` |

## Phase 6: Polish (DONE)

### Mục tiêu

Thêm FAQ, QUICKSTART, polish README cho người mới onboard nhanh.

### Files đã tạo/cập nhật

| Commit | File | Nội dung |
|--------|------|----------|
| `cd09a2b` | `FAQ.md` | 196 dòng, 7 categories |
| `0c5a586` | `QUICKSTART.md` | 137 dòng, 5-min setup + 3 use cases |
| `3bf48ca` | `README.md` (update) | Quick links + structure |

### Bỏ qua

- "When to use" tables per file (đã có trong 01-stack, 02-architecture)
- Thêm Mermaid diagrams vào các file khác (chỉ có ở pipeline/02-sequence, 03-data-model)

---

## Backlog (sau docs)

- Setup Mantine + ApexCharts thực tế trong `web/`
- Migrate 7 pages từ inline style sang Mantine
- Connect SSE log streaming
- Implement dark mode toggle
- Circuit breaker cho LLM API (TODO high)
- Interactive Telegram Bot (Stage 5+)
- Category filtering (Stage 5+)

---

## Notes cho AI agent

Khi soạn docs mới, luôn:
1. Đọc file này trước để biết đang ở phase nào
2. Update file này sau khi commit
3. Tạo 1 commit nhỏ cho mỗi file
4. Push ngay sau commit
5. Update cross-refs trong commit riêng
6. Báo cáo ID commit cho user

---

## Lịch sử thay đổi

- 2026-09-04: Tạo file, lưu kế hoạch soạn docs
- 2026-09-03: Phase 1 (frontend) hoàn thành
- 2026-08-31: Phase 0 (restructure) hoàn thành
