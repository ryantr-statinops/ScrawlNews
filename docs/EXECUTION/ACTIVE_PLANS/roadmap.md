# Active Plan — Roadmap

> Cập nhật: 2026-09-13. ScrawlNews đã hoàn thành phạm vi implementation của Local Release 1.0; operational validation và release hardening đang là công việc kế tiếp.

## Overview

ScrawlNews là **Local Monitor Dashboard** (FastAPI + Celery + Redis + React Vite + Nginx). Newsbot là feature toggle `telegram_enabled`. DB thuần local SQLite. Celery Beat local là production scheduler; GitHub Actions chỉ chạy daily non-delivery smoke (ADR-014).

## Timeline (4 Stages — DONE)

| Stage | Mục tiêu | Deliverable | Status |
|-------|----------|-------------|--------|
| **Stage 1: Foundation** | Scaffold + config + DB thuần local + Go stub | `docker-compose.yml` + `nginx.conf` + `go.mod` + `src/config.py` + `pipeline_runs` migration | ✅ Done `014cc6d`..`c774e8f` |
| **Stage 2: Dashboard MVP** | 3 feature core + BE/FE test cơ bản | `src/api/` + `src/worker/` + `frontend/` Feed/Runs/Config + SSE | ✅ Done `3668fe2`..`45e1851` |
| **Stage 3: Full 6 Features** | Đủ 6 nhóm + FE/BE test tại milestone + quality | Summaries/Delivery/Health/Analytics + Ruff/MyPy | ✅ Done 43 commits `f1cc456`..`b9d0e2c` |
| **Stage 4: Polish + Deploy** | Parity + automation verify | `make dev` Nginx parity + workflow + docs SETUP.md | ✅ Done `0f328aa`..`6a7392c`, `f753937`; scheduler amended by ADR-014 |

**DB thuần local**: SQLite file `sqlite:///data/scrawlnews.db` mount `./data:/app/data`.
**Testing FE+BE**: Có Vitest + Pytest. Verification 2026-09-13: backend 251 passed, 6 skipped, 87% coverage; frontend 11 passed; MyPy, frontend typecheck/lint, Ruff `src/ tests/` và Docker build passed.

---

## Stage 1: Foundation (Scaffold) — DONE `014cc6d`..`c774e8f`

- [x] `requirements.txt` (+celery[redis], redis, fastapi, uvicorn, pydantic-settings) — `d2f6f41`
- [x] `frontend/package.json` (Vite React TS + Mantine + TanStack Router + Vitest) — current frontend
- [x] `docker-compose.yml` + `nginx.conf` (`/api → :8000`, `/ → :5173`, SSE off) — `014cc6d`, `49c0969`
- [x] `Makefile` (install, dev, worker, beat, test, lint) — `13af427`, `cedfbd8`
- [x] `.env.example` (REDIS_URL, CELERY_*, TELEGRAM_ENABLED, DATABASE_URL) — `a5f1700`
- [x] `src/config.py` Pydantic Settings + validator `telegram_enabled` + hot-reload 4 vars — `94e00a8`
- [x] Migration `pipeline_runs` + indexes — `src/repositories/migrate.py`
- [x] `GET/PUT /api/config` + `GET /health` stub — `ceaadb7`
- [x] `go.mod` stub + `cmd/newsctl/main.go` (Cobra) — `341b74f`, `6a7392c`

## Stage 2: Dashboard MVP + Core Pipeline — DONE `3668fe2`..`45e1851`

- [x] Scrawler: RSS fetch + trafilatura + fallback — `65dedb1`
- [x] Synthesizer: OpenAI/OpenRouter batch + fallback raw — `10f8385`
- [x] Messenger: Telegram Bot, split 4096, toggle — `1f68dd0`, `de4d045`
- [x] Celery `pipeline_run` task + FastAPI routes + SSE — `0b9a54c`..`9124808`, `fc072fa`
- [x] React Vite 3 pages (Feed, Runs, Config) + SSE — `d07d62a`
- [x] Tests Stage 2 (BE pytest + FE Vitest) — `45e1851`

## Stage 3: Full 6 Features + Quality — DONE 2026-08-28

- [x] Frontend đủ 6 nhóm (Summaries, Delivery, Health, Analytics) — `frontend/src/routes/`
- [x] Config hot-reload hạn chế 4 vars + persist DB + history — `src/repositories/config_repo.py`, `migrate.py` v2
- [x] SQLite persistence (ArticleRepo, SummaryRepo, PipelineRunRepo) + dedup + cleanup 7 ngày
- [x] Ruff, frontend lint/typecheck/build đã kiểm tra; backend batch test đã được ổn định sau milestone
- [x] Code quality: Ruff, MyPy, pre-commit, ESLint flat — `06b7813`, `b9d0e2c`

## Stage 4: Polish + Deploy — DONE 2026-08-28

- [x] `.github/workflows/scrawlnews.yml` ban đầu chạy production cron — `0f328aa`; chuyển thành daily non-delivery smoke theo ADR-014
- [x] CI: lint + typecheck + tests trên PR — `60b8bba`
- [x] Verify `docker-compose config`, `make dev` parity Nginx, `go run ./cmd/newsctl --help` — `6a7392c`
- [x] SETUP.md + `src/main.py` legacy CLI — `4c32b34`, `e4d43b8`

---

## Stage 5: Product Frontend Cutover — IMPLEMENTED

- [x] Cutover frontend cũ sang frontend mới và repoint compose/nginx/Makefile/CI
- [x] Lấp feature: Feed search/filter + phân trang, Runs polling + cron note, Delivery stat cards, Analytics cost + donut, Config history, Health error board
- [x] Verify `docker-compose up` với `frontend/` mới; dashboard local mở tại `http://localhost`

## Local Release 1.0 — COMPLETE

- [x] Làm pytest chạy ổn định theo batch — 228 passed khi đóng scope; current suite 251 passed, 6 skipped (2026-09-13)
- [x] Chuẩn hóa MyPy theo Python 3.11
- [x] Xử lý graceful Telegram configuration
- [x] Cập nhật setup/testing documentation
- [x] Backup/restore SQLite và dependency audit

## Agent v1 — IMPLEMENTED

- [x] Deterministic Observe → Decide → Act → Verify → Record lifecycle
- [x] SQLite audit trail và correlation ID
- [x] Approval gate cho mọi action
- [x] Auto database backup sau approval
- [x] Pipeline dry-run queue sau approval
- [x] Dashboard Agent tại `/agent`
- [x] `pip-audit` trong CI

## Post-1.0 Roadmap — Reliability First

Scheduler/`--dry-run` và CI hardening đã hoàn thành. Release 1.0 chỉ còn Telegram test delivery validation cần external credentials trước khi đánh dấu operationally validated toàn bộ.

### Release 1.1 — Reliability, Security and Guardrails

| Thứ tự | Deliverable | Exit criteria |
|---|---|---|
| 1 | Frontend toolchain security migration | Vite/Vitest major upgrade có kiểm soát; không còn high/critical `npm audit` finding; build/test pass |
| 2 | Prometheus metrics | Expose run count, duration, errors và pipeline-stage latency; có unit/integration tests |
| 3 | Config validation | Invalid schedule, limit, timezone, URLs và production Telegram config fail fast với public error an toàn |
| 4 | Cost guardrails | Token-to-cost qua configurable price snapshot; monthly estimate và budget alert; không hard-code bảng giá khó update |
| 5 | Source reliability baseline | Report Google News/trafilatura trên nguồn tiếng Việt; chốt fallback và success-rate target |
| 6 | Frontend coverage expansion | Test critical routes/API states, nâng baseline trước khi bật coverage threshold |

### Release 1.2 — Source Expansion

- Chuẩn hóa source adapter interface và canonical article mapping.
- Thêm Hacker News RSS, Reddit và custom RSS với per-source telemetry, timeout, dedup và circuit-breaker behavior.
- Chỉ bắt đầu sau khi Release 1.1 observability/config guardrails hoàn thành.

### Release 1.3 — News Intelligence

- Structured summarization output, similar-story dedup và entity extraction.
- Feedback loop 👍/👎 với audit/opt-out rõ ràng.
- Audio, multilingual và rich Telegram formatting giữ trong backlog cho đến khi có nhu cầu sản phẩm.

## References

- [TASKS/TODO.md](../TASKS/TODO.md) — task cụ thể kế tiếp
- [COMPLETED/changelog.md](../COMPLETED/changelog.md) — developer log
- [ARCHIVED/ideas.md](../ARCHIVED/ideas.md) — backlog ý tưởng
- [PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md](../../PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md) — kiến trúc đích
