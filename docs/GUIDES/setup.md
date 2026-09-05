# Guide — Setup & Usage

> Cách cài đặt, cấu hình, chạy và troubleshoot ScrawlNews.

## Prerequisites

- Python 3.11+
- Node.js (cho web) + npm
- Docker (khuyến nghị) hoặc Redis native
- Git

## Quick Start

```bash
# 1. Clone
git clone https://github.com/ryantr-statinops/ScrawlNews.git
cd ScrawlNews

# 2. Install
make install
# Hoặc manual:
# python -m venv .venv && source .venv/bin/activate
# pip install -r requirements.txt
# playwright install chromium

# 3. Config
cp .env.example .env
# Edit .env với credentials

# 4. Test
make test

# 5. Run — 2 cách 1 terminal
# Docker (có Nginx + Redis):
docker compose up          # → http://localhost (Nginx), :8000/docs (API)
# Local dev parity (cũng qua Nginx :80):
make dev                    # nginx redis Docker + concurrently uvicorn + celery + vite
# CLI:
make run
# Hoặc: PYTHONPATH=. python src/main.py --dry-run
# Go:
go run ./cmd/newsctl --help
```

## Environment Variables (ADR-011)

| Variable | Required | Default | Mô tả |
|----------|----------|---------|-------|
| `APP_ENV` | ❌ | `local` | Môi trường: `local`\|`docker`\|`ci` |
| `TELEGRAM_BOT_TOKEN` | ⚠️ nếu `TELEGRAM_ENABLED=true` | - | Token từ @BotFather |
| `TELEGRAM_CHAT_ID` | ⚠️ nếu `TELEGRAM_ENABLED=true` | - | Chat ID cá nhân hoặc channel |
| `TELEGRAM_ENABLED` | ❌ | `true` | Toggle newsbot feature |
| `LLM_API_KEY` | ✅ | - | API key cho OpenAI |
| `OPENROUTER_API_KEY` | ❌ | - | API key cho OpenRouter/OmniRoute |
| `LLM_PROVIDER` | ❌ | `openrouter` | Provider name |
| `LLM_MODEL` | ❌ | `google/gemma-2-9b-it` | Model name |
| `FETCH_LIMIT` | ❌ | `20` | Max articles per run |
| `SUMMARY_LANG` | ❌ | `vi` | Output language |
| `RETENTION_DAYS` | ❌ | `7` | Data retention |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |
| `DATABASE_URL` | ❌ | `sqlite:///data/scrawlnews.db` | SQLite URL |
| `REDIS_URL` | ❌ | `redis://localhost:6379/0` | Redis (docker: `redis://redis:6379/0`) |
| `CELERY_BROKER_URL` | ❌ | `redis://localhost:6379/0` | Celery broker |
| `CELERY_RESULT_BACKEND` | ❌ | `redis://localhost:6379/1` | Celery result |

Hot reload chỉ 4 vars (`fetch_limit`, `summary_lang`, `telegram_enabled`, `retention_days`) qua `PUT /api/config`. Secrets/connection đổi thì restart.

## Make Commands

| Command | Mô tả |
|---------|-------|
| `make install` | Cài dependencies, Playwright, web deps |
| `make dev` | Dashboard local (uvicorn + celery worker/beat + vite) — 1 terminal |
| `make run` | Pipeline CLI (`python src/main.py`) |
| `make worker` | `celery -A src.worker.celery_app worker` |
| `make beat` | `celery -A src.worker.celery_app beat` |
| `make test` | Chạy tests |
| `make lint` | Ruff lint + format check |
| `make typecheck` | MyPy |
| `make clean` | Xóa cache, data, logs |

## Usage (Run Modes)

```bash
python src/main.py                 # Normal run (gửi Telegram)
python src/main.py --dry-run       # Log console, không gửi
python src/main.py --history       # Xem lịch sử
LOG_LEVEL=DEBUG python src/main.py # Verbose
FETCH_LIMIT=10 SUMMARY_LANG=en python src/main.py  # Override env
```

### GitHub Actions chạy tự động

- 08:00 UTC → 15:00 VN, 12:00 → 19:00, 16:00 → 23:00, 21:00 → 04:00 hôm sau
- Manual: GitHub → Actions → ScrawlNews Daily → Run workflow

### Monitoring

```bash
sqlite3 data/scrawlnews.db "SELECT COUNT(*) FROM articles;"
tail -f logs/scrawlnews.log
```

## Troubleshooting

| Lỗi | Khắc phục |
|-----|-----------|
| `ModuleNotFoundError: No module named 'src'` | Chạy từ root project |
| `TELEGRAM_BOT_TOKEN not set` | Kiểm tra `.env`, không space quanh `=` |
| Playwright browser not found | `playwright install chromium` |
| SQLite "database is locked" | 1 instance; `pkill -f "src/main.py"` |
| LLM API rate limit | Auto retry; giảm `FETCH_LIMIT` |
| Telegram fail | Pipeline save local file, retry next run |
| Lấy TELEGRAM_CHAT_ID | gửi msg bot → `https://api.telegram.org/bot<TOKEN>/getUpdates` → `chat.id` |

## Dependencies (requirements.txt)

```
feedparser>=6.0.10
trafilatura>=1.6.0
openai>=1.0.0
python-telegram-bot>=20.0
pydantic>=2.0.0
python-dotenv>=1.0.0
httpx>=0.25.0
tenacity>=8.2.0
sqlalchemy>=2.0.0
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
celery[redis]>=5.3.0
redis>=5.0.0
playwright>=1.40.0   # optional
pytest, pytest-asyncio, pytest-cov, ruff, mypy, pre-commit  # dev
```

## References

- [testing.md](testing.md) — testing strategy
- [deployment.md](deployment.md) — deploy (GA, Docker, Nginx)
- [PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/04-data-config.md](../PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/04-data-config.md) — config detail
