# 03 — Interface

> Giao diện tương tác: Web UI, API, CLI. Gom tất cả cách người dùng chạm vào hệ thống.

## Principles

- Một terminal parity: `docker compose up` và `make dev` đều qua Nginx `:80`
- Progressive disclosure cho API docs

---

## Dashboard (API + Web)

### API

- `GET /health`, `/api/articles`, `/api/summaries`, `/api/runs`
- `POST /api/runs` trigger Celery
- `PUT /api/config` chỉ 4 biến hot-reload
- `GET /api/config/history` audit
- `GET /api/stats`, `GET /api/logs/stream` (SSE)
- `GET /api/tasks/{id}` Celery task status
- Full spec: `EXECUTION/ACTIVE_PLANS/specs/api.yaml`

### Web

- 7 pages routing: Feed, Summaries, Runs, Delivery, Analytics, Health, Config
- Tech stack chi tiết: xem [frontend/01-stack.md](frontend/01-stack.md) (Mantine UI + ApexCharts + TanStack Router + Zustand + SSE)

### Implementation (Stage 2–4)

- Stage 2: `src/api/routes/articles.py` (q/source filter), `runs.py` (`POST pipeline_run.delay`), `config.py` (limited 4 vars), `health.py`
- Stage 3: `src/api/routes/summaries.py` — `17f63da`, `logs.py` SSE + `stats.py` — `af8a5f7`, web Summaries/Delivery/Health/Analytics — `2332603`..`f1cc456`, `App.tsx` 7 pages — `ef147ab`
- Stage 4: verify `docker-compose config` + `make dev` npx parity — `cedfbd8`
- Nginx: `/api → :8000`, `/ → :5173`, `/api/logs/stream` buffering off

## CLI

### Go newsctl

- `cmd/newsctl/main.go` Cobra stub: `run`, `history` gọi `POST/GET /api/runs`

### Python

- `python src/main.py --dry-run` legacy pipeline (gọi `pipeline_run` trực tiếp không qua Celery)

### Make commands

| Command | Mô tả |
|---------|-------|
| `make install` | Cài dependencies, Playwright, web deps |
| `make dev` | Dashboard local (uvicorn + celery worker/beat + vite) — 1 terminal |
| `make run` | Pipeline CLI (`python src/main.py`) |
| `make worker` | `celery -A src.worker.celery_app worker` |
| `make beat` | `celery -A src.worker.celery_app beat` |
| `make test` | Chạy tests |
| `make lint` | Ruff lint + format check |

## References

- `EXECUTION/ACTIVE_PLANS/specs/api.yaml`
- `src/api/main.py`, `src/api/routes/`
- `web/src/pages/`
- `frontend/` — stack, design tokens, architecture, patterns
- `nginx.conf`
- `go.mod`, `Makefile`
