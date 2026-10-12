# Active Plan — Roadmap

> Cập nhật: 2026-10-04. Local Release 1.0 đã hoàn tất với ngoại lệ Telegram live deferred; Release 1.1 Reliability, Security and Guardrails đã hoàn thành. Xem [integration report](../COMPLETED/reports/2026-10-04-release-1.1-integration.md).

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
**Kiểm thử FE+BE**: Vitest/V8 và Pytest là các CI gate bắt buộc; kết quả Release 1.1 được ghi trong integration report.

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
- [x] Verify `docker-compose up` với `frontend/` mới; dashboard local mở tại `http://localhost:6767`

## Local Release 1.0 — COMPLETE WITH EXCEPTION

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

Scheduler/`--dry-run` và CI hardening đã hoàn thành. Telegram test delivery validation được deferred đến khi có external credentials; runtime local vẫn operational với `TELEGRAM_ENABLED=false`.

### Release 1.1 — COMPLETE (2026-10-04)

| Thứ tự | Deliverable | Kết quả đã xác minh | Trạng thái |
|---|---|---|---|
| 1 | Bảo mật toolchain frontend | Vite/Vitest đã nâng cấp; `npm audit --audit-level=high` không còn high/critical (3 moderate advisory được ghi nhận, không dùng `--force`). | Hoàn thành |
| 2 | Prometheus metrics | `/metrics` trả run counts, durations, errors và stage latency; scrape DB seed/runtime đã xác minh. | Hoàn thành |
| 3 | Config validation | Schedule, limit, timezone, URLs và Telegram production config được validate; invalid multi-key update không ghi partial. | Hoàn thành |
| 4 | Cost guardrails | Price snapshot theo provider/model, monthly estimate và warning-only budget alert; runtime đã xác minh. | Hoàn thành |
| 5 | Source reliability baseline | 12 category requests, RSS 12/12; extraction 0/240, `fallback_target` và recommendation được ghi trong report. | Hoàn thành |
| 6 | Frontend coverage | V8 gate tối thiểu 80% cho lines/statements/functions/branches; đo được 99.87%/99.87%/84.23%/92.20%. | Hoàn thành |

### Release 1.2 — Source Expansion

- Chuẩn hóa source adapter interface và canonical article mapping.
- Thêm Hacker News RSS, Reddit và custom RSS với per-source telemetry, timeout, dedup và circuit-breaker behavior.
- Các guardrails Release 1.1 đã được xác minh; điều kiện tiên quyết này hoàn thành. Release 1.2 Source Expansion là giai đoạn kế tiếp theo roadmap.

### Release 1.3 — News Intelligence

- Structured summarization output, similar-story dedup và entity extraction.
- Feedback loop 👍/👎 với audit/opt-out rõ ràng.
- Audio, multilingual và rich Telegram formatting giữ trong backlog cho đến khi có nhu cầu sản phẩm.

## References

- [TASKS/TODO.md](../TASKS/TODO.md) — task cụ thể kế tiếp
- [COMPLETED/changelog.md](../COMPLETED/changelog.md) — developer log
- [ARCHIVED/ideas.md](../ARCHIVED/ideas.md) — backlog ý tưởng
- [PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md](../../PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md) — kiến trúc đích
