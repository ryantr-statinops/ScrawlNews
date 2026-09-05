# Target Architecture — Project muốn trở thành như thế nào

> Kiến trúc đích của ScrawlNews. Phần lớn đã implement ở Stage 1–4; phần "Future" là hướng phát triển.

## System Blocks (Dashboard-first, ADR-011)

```
Nginx :80
  /        -> Vite React :5173
  /api     -> FastAPI :8000 -> Celery Beat -> Redis -> Worker -> Pipeline -> SQLite
GitHub Actions cron 0 8,12,16,21 * * * -> pipeline (không cần dashboard) -> SQLite
```

- Dashboard là entrypoint quan sát, Celery là execution engine
- Api, worker, beat, redis, web, nginx chạy qua `docker-compose.yml`
- `make dev` cũng chạy nginx + redis trong Docker để parity
- Storage thuần local, không Turso

## High-Level Component Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│  Nginx (:80) → / → Vite React (web)                                  │
│              → /api → FastAPI (src/api)                               │
│                        │  ┌──────────────┐  ┌──────────────────┐     │
│                        ├──│  Scrawler    │  │  Synthesizer     │     │
│                        │  │  Service     │  │  Service         │     │
│                        │  └──────┬───────┘  └──────┬───────────┘     │
│                        │         │                 │                  │
│                        │  ┌──────────────┐  ┌──────────────┐         │
│                        ├──│ArticleRepo   │  │SummaryRepo   │         │
│                        │  │(SQLite)      │  │(SQLite)      │         │
│                        │  └──────────────┘  └──────────────┘         │
│                        │         ▲                 ▲                  │
│                        │  ┌──────────────┐  ┌──────────────┐         │
│                        │  │   Config     │  │ Celery+Redis │         │
│                        │  │ (Pydantic)   │  │ Beat/Worker  │         │
│                        │  └──────────────┘  └──────┬───────┘         │
│                        │                           │                  │
│                        │  ┌──────────────────┐     │                  │
│                        └──│   Messenger      │◄────┘                  │
│                           │ (feature toggle) │                        │
│                           └──────────────────┘                        │
│  docker-compose: api + worker + beat + redis + web + nginx            │
│  make dev: concurrently uvicorn + celery worker/beat + vite           │
└──────────────────────────────────────────────────────────────────────┘
```

## Principles

- **Dashboard-first**: mọi thao tác quan sát và điều khiển qua dashboard (ADR-011)
- **Pure local**: SQLite file mount `./data:/app/data`, không phụ thuộc service ngoài
- **Hot-reload hạn chế**: chỉ 4 biến đơn giản qua `PUT /api/config` (ADR-013)
- **Flat SKILL tagging**: `.agent/SKILL/<skill>/SKILL.md` với `metadata.tags`
- **Progressive disclosure 3 levels** cho docs và skills

## Deployment Architecture (tổng, DB thuần local)

```
Local: Nginx (:80) → / → Vite React, /api → FastAPI → Celery Beat → Redis → Worker → SQLite file
GitHub Actions (free) → cron 4 lần/ngày → pipeline (không cần dashboard) → OmniRoute → OpenRouter → SQLite file
Tổng chi phí: $0/tháng (Redis/Nginx local, không hosting)
```

### Deployment Options

| Option | Lệnh | Pros | Cons |
|--------|------|------|------|
| docker compose | `docker compose up` | Reproducible, có Nginx + Redis | Cần Docker |
| make dev | `make dev` | Không Docker, concurrently uvicorn+celery+vite | Phụ thuộc local Python/Node |

### Hosting / DB Options (tham khảo)

- **OmniRoute host**: Fly.io free tier (3 shared VMs, 256MB RAM) — ADR-010
- **Database**: SQLite local cho Stage 1–4; Turso chỉ nếu cần remote (ADR-010)

## Future (Stage 5+)

| Feature | Effort | Priority |
|---------|--------|----------|
| Interactive Telegram Bot | Medium | High |
| Category Filtering | Low | High |
| Multi-source (HN, Reddit) | Medium | Medium |
| Cost Tracking chi tiết | Low | Medium |
| Audio Newsletter (TTS) | Medium | Low |
| Go fetcher sidecar (nếu cần) | Medium | Low |

## References

- [DECISIONS.md](DECISIONS.md) — ADR-011/012/013
- [DOMAIN_CONCEPTS/02-core-engine.md](DOMAIN_CONCEPTS/02-core-engine.md) — service interfaces
- [DOMAIN_CONCEPTS/04-data-config.md](DOMAIN_CONCEPTS/04-data-config.md) — data model, repository
- [EXECUTION/ACTIVE_PLANS/roadmap.md](../EXECUTION/ACTIVE_PLANS/roadmap.md) — lộ trình theo stage
