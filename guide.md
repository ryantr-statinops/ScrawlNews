# Local Guide — Khởi tạo ScrawlNews

Hướng dẫn khởi tạo local cho ScrawlNews Dashboard (1 terminal, Nginx parity).

## 1. Yêu cầu

- Python 3.11+ (`python3 --version`)
- Node 20+ (`node --version`)
- Docker + docker-compose v1 (`docker-compose --version`) — máy hiện tại dùng `docker-compose` hyphen, không phải `docker compose` space
- Git

## 2. Clone và cd

Mọi lệnh phải chạy từ **workspace root**:

```bash
cd ~/Projects/ScrawlNews
pwd  # phải ra .../ScrawlNews
ls   # phải thấy Makefile, docker-compose.yml, src/, web/
```

Không `cd` vào `src/` hay `web/` để chạy `make`.

## 3. Chuẩn bị env

```bash
cp .env.example .env
# Edit .env nếu có LLM_API_KEY, TELEGRAM_BOT_TOKEN
# Để trống vẫn chạy: Synthesizer fallback raw titles, Messenger skip nếu telegram_enabled=false
```

Lưu ý: `cp .env.example` thiếu đích sẽ báo `missing destination`, phải đủ `cp .env.example .env`.

## 4. Cài đặt

```bash
# Cách đã fix cho Ubuntu PEP 668 (externally-managed-environment)
pip install --break-system-packages -r requirements.txt
# hoặc dùng venv nếu có python3-venv: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Web deps
cd web && npm install && cd ..

# Playwright (optional, cho fallback)
playwright install chromium || true
```

Hoặc dùng:

```bash
make install
# Makefile:4 đã fix pip --break-system-packages cho bạn
```

## 5. Chạy

### Option A: Docker (khuyến nghị, reproducible)

```bash
docker-compose build
docker-compose up
# http://localhost              -> Nginx :80
# http://localhost:8000/docs    -> FastAPI docs
```

Lần đầu build gửi 286MB context và pull python:3.11-slim, redis:7-alpine, mất 5-10 phút. Lần sau dùng cache, 10-30s.

### Option B: Local parity (nhanh, 1 terminal)

```bash
make dev
# Makefile:9 sẽ: docker-compose up -d nginx redis
# + npx concurrently uvicorn :8000 --reload + celery worker + celery beat + vite :5173
# Vẫn qua Nginx :80 nên http://localhost giống Option A
```

Nếu gặp `unknown shorthand flag: 'd' in -d` là do dùng `docker compose` space, đã fix thành `docker-compose` hyphen trong Makefile:9.

Nếu gặp `externally-managed-environment` là do pip PEP 668, đã fix bằng `--break-system-packages`.

## 6. Verify

```bash
curl http://localhost:8000/health
# {"status":"ok","db":"ok","redis":"ok"}

curl http://localhost/api/articles
# {"count":0,"articles":[]}

curl -X POST http://localhost:8000/api/runs -H "Content-Type: application/json" -d '{}'
# {"task_id":"...","status":"pending"}

# Web: http://localhost -> 7 tabs Feed/Summaries/Runs/Delivery/Analytics/Health/Config
```

CLI không cần dashboard:

```bash
PYTHONPATH=. python src/main.py --dry-run --limit 5
go run ./cmd/newsctl --help
```

## 7. Troubleshooting

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `cp: missing destination` | Gõ thiếu `.env` đích | `cp .env.example .env` |
| `externally-managed-environment` | Ubuntu PEP 668 | `pip install --break-system-packages` hoặc venv |
| `unknown shorthand flag: 'd'` | `docker compose` vs `docker-compose` | Dùng `docker-compose` hyphen, đã fix Makefile:9 |
| `No such file: .env` | Chưa `cp` | `cp .env.example .env` trước `docker-compose config` |
| `ModuleNotFoundError: No module named 'src'` | Chạy `python src/main.py` từ sai thư mục | `PYTHONPATH=. python src/main.py` từ root |

## 8. Dừng

```bash
# Nếu đang docker-compose up (full)
Ctrl+C
docker-compose down

# Nếu đang make dev
Ctrl+C  # dừng concurrently (uvicorn/celery/vite) + nginx/redis vẫn chạy detached
docker-compose down
```

## 9. Docs liên quan

- README.md - tổng quan
- SETUP.md - setup ngắn gọn
- docs/README.md - documentation map and reading guide
- docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/ - core concepts
