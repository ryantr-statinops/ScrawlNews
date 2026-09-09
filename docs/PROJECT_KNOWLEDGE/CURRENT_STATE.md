# Current State — Project đang thực sự như thế nào

> Cập nhật: 2026-09-09. Stage 1–4 và phần lớn Stage 5 đã hoàn tất. File này mô tả trạng thái thực tế của codebase, không phải kế hoạch.

## Purpose

ScrawlNews là **Local Monitor Dashboard** cho tin tức. Dashboard là service chính chạy local (1 terminal); newsbot (thu thập → tóm tắt → Telegram) chỉ là 1 feature toggle (`telegram_enabled`).

## Đã build được gì

| Stage | Mục tiêu | Status |
|-------|----------|--------|
| Stage 1: Foundation | Scaffold + config + DB thuần local + Go stub | ✅ Done `014cc6d`..`c774e8f` |
| Stage 2: Dashboard MVP | 3 page core + Celery pipeline + BE/FE test cơ bản | ✅ Done `3668fe2`..`45e1851` |
| Stage 3: Full 6 Features | Đủ 6 nhóm + FE/BE 77 passed + quality | ✅ Done 43 commits `f1cc456`..`b9d0e2c` |
| Stage 4: Polish + Deploy | Nginx parity verify + GA + SETUP.md | ✅ Done `0f328aa`..`6a7392c`, `f753937` |
| Stage 5: Product Frontend Cutover | Frontend mới + Telegram bot + category filtering + circuit breaker | ✅ Implemented; local runtime verified |

## Trạng thái kỹ thuật hiện tại

### Infra (Stage 1)
- `docker-compose.yml` 6 services: api + worker + beat + redis + web + nginx — `014cc6d`
- `nginx.conf` routing `/api → :8000`, `/ → :5173`, SSE buffering off — `49c0969`, `1e18b382`
- `Dockerfile` python:3.11-slim — `976ebda`
- `.github/workflows` cron `0 8,12,16,21 * * *` + CI — `0f328aa`..`60b8bba`

### Backend (Stage 2–3)
- FastAPI routes split: articles, summaries, runs, config, health, stats, logs (SSE) — `17f63da`..`af8a5f7`
- Celery `pipeline.run` task thực tế, max_retries 3 — `9124808`
- `ConfigRepository` + migrate v2 (settings/config_history) — `afa00a7`
- Scrawler (feedparser + trafilatura), Synthesizer (OpenRouter batch), Messenger (Telegram toggle) — `65dedb1`..`1f68dd0`

### Frontend (product, đã cutover)
- `frontend/` là web chính: Mantine UI v7, TanStack Router, ApexCharts, Zustand, SSE logs — xem `DOMAIN_CONCEPTS/frontend/01-stack.md`. Chạy `:5173`, nối `docker-compose.yml` + `Makefile` + CI
- MVP cũ (`web/` react-router-dom + recharts + tailwind) đã xóa sau cutover (`8593dd5f`), xem lại qua git history nếu cần

### Verify (Stage 4)
- `docker-compose config` passed với .env
- `go run ./cmd/newsctl --help` ok — `6a7392c`
- `pytest tests/unit -q` = 77 passed, `pytest tests/integration -q` = 10 passed, `ruff` passed

## Cấu trúc source thực tế

```
ScrawlNews/
├── docker-compose.yml      # api + worker + beat + redis + web + nginx
├── nginx.conf              # /api → :8000, / → :5173, SSE off
├── Makefile                # install, dev, worker, beat, run, test, lint
├── go.mod + cmd/newsctl/   # Go Cobra stub (run/history gọi API)
├── src/
│   ├── main.py             # Legacy CLI + Pipeline class
│   ├── config.py           # Pydantic Settings (ADR-011)
│   ├── models/             # article, summary, run
│   ├── services/           # base, scrawler, synthesizer, messenger
│   ├── repositories/       # article_repo, summary_repo, run_repo, config_repo, migrate
│   ├── api/                # FastAPI app + routes/
│   ├── worker/             # celery_app, tasks
│   └── utils/              # retry, formatter, logging
├── frontend/               # React Vite dashboard chính
├── tests/                  # unit (77) + integration (10)
└── data/ logs/             # SQLite volume + logs (gitignored)
```

## Known limitations (chưa làm)

- Prometheus metrics chưa có
- `pip-audit` chưa chạy trong CI
- Multi-source, detailed cost tracking và structured summarization chưa làm.
- Telegram cần token hợp lệ nếu bật; dashboard vẫn chạy được với `TELEGRAM_ENABLED=false`.
- Backend pytest vẫn cần điều tra hiện tượng treo khi chạy theo batch; local Docker dashboard đã chạy được.

## References

- [TARGET_ARCHITECTURE.md](TARGET_ARCHITECTURE.md) — kiến trúc đích
- [DOMAIN_CONCEPTS/](DOMAIN_CONCEPTS/) — chi tiết từng domain
- [EXECUTION/ACTIVE_PLANS/roadmap.md](../EXECUTION/ACTIVE_PLANS/roadmap.md) — kế hoạch theo stage
- [EXECUTION/COMPLETED/changelog.md](../EXECUTION/COMPLETED/changelog.md) — developer log chi tiết
