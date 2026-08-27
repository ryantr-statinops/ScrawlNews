# ScrawlNews

Local Monitor Dashboard for news — newsbot is a feature toggle. 1 terminal local hosting.

## Stack

| Layer | Technology |
|-------|-----------|
| **Scrawler** | Python + RSS (feedparser) + Trafilatura/Readability |
| **Synthesizer** | OpenAI / OpenRouter / OmniRoute |
| **Messenger** | Telegram Bot API — `telegram_enabled` toggle (feature) |
| **Dashboard** | FastAPI + Celery + Redis + React 18 + TS + Vite + Nginx |

## Quick Start (1 terminal)

```bash
# Docker (khuyến nghị, có Nginx + Redis)
docker compose up  # → http://localhost, http://localhost:8000/docs

# hoặc không Docker
make install
cp .env.example .env
make dev           # uvicorn + celery worker/beat + vite concurrently

# CLI pipeline vẫn chạy
make run           # hoặc python src/main.py --dry-run
```

See `docs/plan/INDEX.md` for reading guide, `docs/plan/PLAN.md` for architecture.

## Dashboard Features (6 groups)

Feed Monitor, Summarization Monitor, Pipeline Control, Delivery Monitor, System/Health, Analytics — see `docs/plan/PLAN.md:10` and `spec/api.yaml`.

## Skills (legacy)

| Skill | Technology | Description |
|-------|-----------|-------------|
| **Scrawler** | feedparser + Trafilatura | Fetch articles from Google News RSS |
| **Synthesizer** | OpenAI / LLM | Summarize articles into key points |
| **Messenger** | Telegram Bot API | Deliver summaries (toggle) |
