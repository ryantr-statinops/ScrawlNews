# 03 — Interface

> Giao diện tương tác: Web UI, API, CLI. Gom tất cả cách người dùng chạm vào hệ thống.

## Principles

- Một terminal parity: `docker-compose up` và `make dev` đều qua Nginx nội bộ `:80`, host dashboard mặc định `:6767`
- Progressive disclosure cho API docs

---

## Dashboard (API + Web)

### API

- `GET /health`, `/api/articles`, `/api/summaries`, `/api/runs`
- `POST /api/runs` trigger Celery
- `PUT /api/config` cập nhật runtime settings được allow-list
- `GET /api/config/history` audit
- `GET /api/stats` legacy-compatible, `GET /api/logs/stream` (SSE)
- Analytics Command Center: `GET /api/analytics/{overview|content|pipeline|sources|ai-usage|drilldown}`
- Analytics query dùng `window=1h|4h|12h|24h|7d|30d`; filter tùy endpoint gồm `category`, `source_id`, `provider`, `model`, `country`
- `GET /api/tasks/{id}` Celery task status
- Full spec: `EXECUTION/ACTIVE_PLANS/specs/api.yaml`

### Web

- 7 trang chính: Feed, Summaries, Runs, Delivery, Analytics, Settings, Agent. Route Health và Config cũ vẫn được giữ tương thích.
- Analytics có 5 tab: Overview, Content, Pipeline, Sources và AI Usage; filter được lưu trong URL, KPI so với kỳ trước và click mở drawer drill-down.
- Feed dùng workspace 2 cột: utility rail bên trái (Agent ở trên, Topic digests ở dưới), article table bên phải; trên mobile chuyển thành một cột. Digest/summary render GFM Markdown an toàn. Agent hiện là mock panel frontend, chưa gọi backend thật; chỉ có message input và nút mũi tên để thu gọn/mở rộng. Khi thu gọn, panel giữ header tối thiểu 48px và khoảng cách 16px với Topic digests. Article mở detail drawer bên phải; digest mở detail drawer bên trái kèm source articles và lịch sử digest.
- Tech stack chi tiết: xem [frontend/01-stack.md](frontend/01-stack.md) (Mantine UI + ApexCharts + TanStack Router + Zustand + SSE)

### Implementation (Stage 2–4)

- Stage 2: `src/api/routes/articles.py` (q/source filter), `runs.py` (`POST pipeline_run.delay`), `config.py` (limited 4 vars), `health.py`
- Stage 3: `src/api/routes/summaries.py` — `17f63da`, `logs.py` SSE + `stats.py` — `af8a5f7`, web Summaries/Delivery/Health/Analytics — `2332603`..`f1cc456`, `App.tsx` 7 pages — `ef147ab`
- Stage 4: verify `docker-compose config` + `make dev` npx parity — `cedfbd8`
- Command Center: analytics service/API — `8c9b4f98`..`07ce9b93`; 5 tab và shared filters — `9bc36dc7`..`547385c5`
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
- `frontend/src/routes/`
- `frontend/` — stack, design tokens, architecture, patterns
- `nginx.conf`
- `go.mod`, `Makefile`
