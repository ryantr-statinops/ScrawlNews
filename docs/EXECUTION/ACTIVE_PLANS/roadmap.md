# Active Plan — Roadmap

> Kế hoạch đang thực hiện. Stage 1–4 đã DONE (2026-08-28). Stage 5+ là hướng phát triển tiếp theo.

## Overview

ScrawlNews là **Local Monitor Dashboard** (FastAPI + Celery + Redis + React Vite + Nginx). Newsbot là feature toggle `telegram_enabled`. DB thuần local SQLite. Pipeline chạy qua GitHub Actions cron 4x/ngày + Celery Beat local.

## Timeline (4 Stages — DONE)

| Stage | Mục tiêu | Deliverable | Status |
|-------|----------|-------------|--------|
| **Stage 1: Foundation** | Scaffold + config + DB thuần local + Go stub | `docker-compose.yml` + `nginx.conf` + `go.mod` + `src/config.py` + `pipeline_runs` migration | ✅ Done `014cc6d`..`c774e8f` |
| **Stage 2: Dashboard MVP** | 3 feature core + BE/FE test cơ bản | `src/api/` + `src/worker/` + `web/` Feed/Runs/Config + SSE | ✅ Done `3668fe2`..`45e1851` |
| **Stage 3: Full 6 Features** | Đủ 6 nhóm + FE/BE 77 passed + quality | Summaries/Delivery/Health/Analytics + Ruff/MyPy | ✅ Done 43 commits `f1cc456`..`b9d0e2c` |
| **Stage 4: Polish + Deploy** | Parity + GA verify | `make dev` Nginx parity + GA cron + docs SETUP.md | ✅ Done `0f328aa`..`6a7392c`, `f753937` |

**DB thuần local**: Stage 1–4 đều dùng `SQLite file` `sqlite:///data/scrawlnews.db` mount `./data:/app/data`.
**Testing FE+BE**: Stage 2–3 đều có Vitest + Pytest — 77 passed + 10 integration.

---

## Stage 1: Foundation (Scaffold) — DONE `014cc6d`..`c774e8f`

- [x] `requirements.txt` (+celery[redis], redis, fastapi, uvicorn, pydantic-settings) — `d2f6f41`
- [x] `web/package.json` (Vite React TS + TanStack Query + Recharts + Tailwind + Vitest) — `38e924d`
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

- [x] Web đủ 6 nhóm (Summaries, Delivery, Health, Analytics) — 43 commits, `web/src/App.tsx`
- [x] Config hot-reload hạn chế 4 vars + persist DB + history — `src/repositories/config_repo.py`, `migrate.py` v2
- [x] SQLite persistence (ArticleRepo, SummaryRepo, PipelineRunRepo) + dedup + cleanup 7 ngày
- [x] Tests full FE+BE 77 passed + 10 integration, ruff passed, web lint flat — `b9d0e2c`
- [x] Code quality: Ruff, MyPy, pre-commit, ESLint flat — `06b7813`, `b9d0e2c`

## Stage 4: Polish + Deploy — DONE 2026-08-28

- [x] `.github/workflows/scrawlnews.yml` cron `0 8,12,16,21 * * *` + `workflow_dispatch` — `0f328aa`
- [x] CI: lint + typecheck + tests trên PR — `60b8bba`
- [x] Verify `docker-compose config`, `make dev` parity Nginx, `go run ./cmd/newsctl --help` — `6a7392c`
- [x] SETUP.md + `src/main.py` legacy CLI — `4c32b34`, `e4d43b8`

---

## Stage 5+: Mở rộng (Post-MVP)

| Feature | Effort | Priority |
|---------|--------|----------|
| Interactive Telegram Bot | Medium | High |
| Category Filtering | Low | High |
| Multi-source (HN, Reddit) | Medium | Medium |
| Cost Tracking chi tiết | Low | Medium |
| Audio Newsletter (TTS) | Medium | Low |
| Go fetcher sidecar (nếu cần) | Medium | Low |

## References

- [TASKS/TODO.md](../TASKS/TODO.md) — task cụ thể kế tiếp
- [COMPLETED/changelog.md](../COMPLETED/changelog.md) — developer log
- [ARCHIVED/ideas.md](../ARCHIVED/ideas.md) — backlog ý tưởng
- [PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md](../../PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md) — kiến trúc đích
