# Quickstart

> Hướng dẫn nhanh để chạy ScrawlNews trong 5 phút. Cập nhật 2026-09-04.

## 5 phút setup

### Bước 1: Prerequisites (1 phút)

```bash
python3 --version   # >= 3.11
node --version      # >= 18
docker --version    # >= 20.10
```

Nếu thiếu, cài:
- Python: https://www.python.org/downloads/
- Node: https://nodejs.org/
- Docker: https://docs.docker.com/get-docker/

### Bước 2: Clone + Install (2 phút)

```bash
git clone https://github.com/ryantr-statinops/ScrawlNews.git
cd ScrawlNews

# Cài dependencies (BE + FE + Playwright)
make install
```

### Bước 3: Configure (30s)

```bash
cp .env.example .env
```

Mở `.env` và điền (ít nhất):
```bash
LLM_API_KEY=sk-...              # Bắt buộc (OpenAI)
OPENROUTER_API_KEY=sk-or-...    # OpenRouter (free models)
# TELEGRAM_BOT_TOKEN=...        # Optional, nếu muốn gửi Telegram
# TELEGRAM_CHAT_ID=...          # Optional
```

### Bước 4: Run (1 phút)

```bash
make dev
# → http://localhost
```

Dashboard sẽ hiện ở `http://localhost`. Click "Run Now" để test pipeline.

### Bước 5: Verify (30s)

```bash
curl http://localhost:8000/health
# {"status":"ok","db":"ok","redis":"ok"}
```

```bash
curl -X POST http://localhost/api/runs -H "Content-Type: application/json" -d '{}'
# {"run_id":"...","task_id":"...","status":"pending"}
```

## 3 use case phổ biến

### Use case 1: Chỉ monitor dashboard (không gửi Telegram)

```bash
# .env
TELEGRAM_ENABLED=false
```

Pipeline vẫn chạy, articles/summaries lưu DB, xem qua web.

### Use case 2: Newsletter tự động qua Telegram

```bash
# .env
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=<token từ @BotFather>
TELEGRAM_CHAT_ID=<chat id của bạn>
```

Lấy chat ID: gửi message cho bot, truy cập
`https://api.telegram.org/bot<TOKEN>/getUpdates`, tìm `chat.id`.

### Use case 3: Dùng free LLM model (không tốn tiền)

```bash
# .env
LLM_PROVIDER=openrouter
LLM_MODEL=google/gemma-2-9b-it
OPENROUTER_API_KEY=sk-or-...
```

Đăng ký key free tại https://openrouter.ai/.

## Các lệnh hay dùng

```bash
make dev               # Chạy dashboard
make run               # Chạy pipeline 1 lần (CLI)
make test              # Chạy tests
make lint              # Lint code
docker compose up      # Chạy full Docker stack
docker compose down    # Stop Docker
docker compose logs    # Xem logs
```

## Cấu trúc nhanh

```
ScrawlNews/
├── src/                # Backend (Python)
│   ├── api/            # FastAPI routes
│   ├── services/       # Scrawler, Synthesizer, Messenger
│   ├── repositories/   # SQLite access
│   ├── worker/         # Celery tasks
│   └── config.py       # Settings
├── web/                # Frontend (React)
│   └── src/pages/      # 7 dashboard pages
├── docs/               # Documentation
├── data/               # SQLite database
├── logs/               # Application logs
├── .env                # Environment (gitignored)
└── Makefile            # Common commands
```

## Đọc tiếp

- **Hiểu project**: [docs/README.md](../README.md)
- **Setup chi tiết**: [docs/GUIDES/setup.md](../GUIDES/setup.md)
- **Deploy**: [docs/GUIDES/deployment.md](../GUIDES/deployment.md)
- **FAQ**: [docs/PROJECT_KNOWLEDGE/FAQ.md](FAQ.md)
- **Glossary**: [docs/PROJECT_KNOWLEDGE/GLOSSARY.md](GLOSSARY.md)
- **ADRs**: [docs/PROJECT_KNOWLEDGE/DECISIONS.md](DECISIONS.md)
