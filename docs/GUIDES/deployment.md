# Guide — Deployment

> Cách deploy ScrawlNews: Local Dashboard (Docker/Nginx) + Celery Beat production scheduler + GitHub Actions scheduled smoke.

## Overview

- **Primary scheduler**: Celery Beat local, dùng chung Redis/worker/SQLite với dashboard.
- **Local monitor**: `docker-compose up` (api + worker + beat + redis + web + nginx) hoặc `make dev` (uvicorn + celery + vite, parity Nginx).
- **Scheduled smoke**: GitHub Actions một lần/ngày, dry-run không LLM/Telegram secrets trên SQLite tạm.
- **Cost**: $0/tháng (Redis/Nginx local, GA free).

## Local Dashboard (Nginx + Celery, ADR-011/012)

```yaml
# docker-compose.yml (1 terminal: docker-compose up)
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  api:
    build: .
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
    env_file: .env
    depends_on: [redis]
    volumes: ["./data:/app/data"]
  worker:
    build: .
    command: celery -A src.worker.celery_app worker --loglevel=info
    env_file: .env
    depends_on: [redis, api]
  beat:
    build: .
    command: celery -A src.worker.celery_app beat --loglevel=info
    env_file: .env
    environment:
      DATABASE_URL: sqlite:///data/scrawlnews.db
    depends_on: [redis]
    volumes: ["./data:/app/data"]
  web:
    build: ./frontend
    ports: ["5173:5173"]
  nginx:
    image: nginx:alpine
    ports: ["6767:80"]
    volumes: ["./nginx.conf:/etc/nginx/nginx.conf:ro"]
    depends_on: [api, web]
```

```nginx
# nginx.conf
upstream api { server api:8000; }
upstream web { server web:5173; }
server {
  listen 80;
  location /api/ { proxy_pass http://api; }
  location / { proxy_pass http://web; }
  location /api/logs/stream { proxy_pass http://api; proxy_buffering off; }
}
```

```bash
# Make dev (parity Nginx trong Docker):
make dev   # docker-compose dev services + concurrently uvicorn + celery worker/beat + vite
make worker
make beat
go run ./cmd/newsctl --help   # Cobra stub
```

## GitHub Actions Scheduled Smoke

```yaml
# .github/workflows/scrawlnews.yml
name: ScrawlNews Scheduled Smoke
on:
  schedule:
    - cron: '0 1 * * *'
  workflow_dispatch:
jobs:
  pipeline-smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: |
          pip install -r requirements.txt
          playwright install chromium
      - env:
          DATABASE_URL: sqlite:////tmp/scrawlnews-smoke.db
          TELEGRAM_ENABLED: "false"
          LLM_API_KEY: ""
          OPENROUTER_API_KEY: ""
        run: python -m src.main --dry-run --limit 3
```

Workflow này không dùng production secrets. SQLite trên runner là tạm và không xuất hiện trong dashboard local.

## Hosting / DB Options (tham khảo, ADR-010)

| Component | Free tier | Phù hợp |
|-----------|-----------|---------|
| OmniRoute host: Fly.io | 3 shared VMs, 256MB RAM | ✅ Free, ổn định |
| Render | Free web, 512MB | ⚠️ Spin-down 15min |
| Railway | — | ❌ $5/tháng |
| Database: SQLite local | File-based | ✅ Current local architecture |
| Turso | 5GB free | ✅ Nếu cần remote (Phase 2+) |

## Deployment Architecture (tổng, DB thuần local)

```
Local: Nginx (:6767 host/:80 container) → / → Vite React, /api → FastAPI → Celery Beat → Redis → Worker → SQLite file
GitHub Actions (free) → daily RSS/fallback smoke → temporary SQLite; không production delivery
```

## Verify Checklist (Stage 4)

- [x] `docker-compose config` passed với .env
- [ ] `make dev` parity Nginx ok
- [ ] `go run ./cmd/newsctl --help` ok
- [ ] `pytest` + `npm run test` green
- [ ] Scheduled smoke chạy ít nhất 1 lần thành công

## References

- [setup.md](setup.md) — cấu hình env, Make commands
- [PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md](../PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md) — deployment architecture
- `EXECUTION/ACTIVE_PLANS/specs/api.yaml` — endpoints
