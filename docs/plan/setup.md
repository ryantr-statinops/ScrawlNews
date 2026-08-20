# Setup

Hướng dẫn cài đặt và chạy ScrawlNews trên môi trường local.

## Prerequisites

- **Python 3.11+** (recommended 3.11 or 3.12)
- **pip** (package manager)
- **Git** (để clone repo)
- (Optional) **Playwright browsers** nếu dùng scraping fallback mode

## Quick Start

```bash
# 1. Clone repo
git clone https://github.com/ryantr-statinops/ScrawlNews.git
cd ScrawlNews

# 2. Install dependencies
make install

# 3. Cấu hình environment
cp .env.example .env
# Edit .env với credentials của bạn

# 4. Chạy test
make test

# 5. Chạy agent
make run
```

## Project Structure (sau khi setup)

```
ScrawlNews/
├── .env                    # Local config (không commit)
├── .env.example            # Template config
├── Makefile                # Commands: install, run, test, lint
├── requirements.txt        # Python dependencies
├── src/
│   ├── main.py             # Entry point
│   ├── config.py           # Pydantic Settings
│   ├── models/             # Data models
│   ├── services/           # 3 Skills services
│   ├── repositories/       # SQLite repos
│   └── utils/              # Helpers
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── data/
│   └── scrawlnews.db       # SQLite database (auto-created)
├── logs/                   # Application logs
└── .github/workflows/      # CI/CD (Phase 3)
```

## Install Details

### make install

```bash
make install
```

Thực hiện:
1. `pip install --upgrade pip`
2. `pip install -r requirements.txt`
3. `playwright install chromium` (cho fallback scraper)
4. Tạo thư mục `data/`, `logs/` nếu chưa có

### Manual Install

```bash
# Tạo virtual env (khuyến nghị)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install deps
pip install --upgrade pip
pip install -r requirements.txt

# Playwright browsers (optional, for fallback)
playwright install chromium
```

## Configuration

### .env.example

```bash
# Telegram Bot (required)
TELEGRAM_BOT_TOKEN=123456789:ABC-DEF_GHIjklMNOpqrSTUvwxyz
TELEGRAM_CHAT_ID=-1001234567890

# LLM Provider (required)
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Optional tuning
FETCH_LIMIT=20
SUMMARY_LANG=vi
RETENTION_DAYS=7
LOG_LEVEL=INFO
```

### Cách lấy Credentials

| Credential | Cách lấy |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | Chat với [@BotFather](https://t.me/BotFather) → `/newbot` → copy token |
| `TELEGRAM_CHAT_ID` | Gửi tin nhắn cho bot → truy cập `https://api.telegram.org/bot<TOKEN>/getUpdates` → tìm `chat.id` |
| `LLM_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) → Create new secret key |

## Commands (Makefile)

| Command | Mô tả |
|---------|-------|
| `make install` | Cài đặt dependencies, Playwright |
| `make run` | Chạy pipeline chính |
| `make test` | Chạy tất cả tests (unit + integration) |
| `make test-unit` | Chỉ unit tests |
| `make test-int` | Chỉ integration tests |
| `make lint` | Ruff lint + format check |
| `make format` | Ruff auto-format code |
| `make typecheck` | MyPy type checking |
| `make clean` | Xóa cache, .pyc, data/*.db, logs/* |
| `make help` | Hiển thị tất cả commands |

## Run Modes

### Normal Run (gửi Telegram)

```bash
make run
# hoặc
python src/main.py
```

### Dry Run (không gửi Telegram, log ra console)

```bash
python src/main.py --dry-run
```

### Xem Lịch Sử

```bash
python src/main.py --history
```

### Debug Mode (verbose logging)

```bash
LOG_LEVEL=DEBUG python src/main.py
```

## Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'src'"

```bash
# Chạy từ root directory của project
cd /path/to/ScrawlNews
python src/main.py
```

### Lỗi: "TELEGRAM_BOT_TOKEN not set"

```bash
# Kiểm tra .env tồn tại và có đúng format
cat .env
# Đảm bảo không có spaces quanh dấu =
```

### Lỗi: Playwright browser not found

```bash
playwright install chromium
# Hoặc cài full browsers
playwright install
```

### Lỗi: SQLite "database is locked"

```bash
# Chỉ chạy 1 instance tại một thời điểm
# Kiểm tra process: ps aux | grep python
# Kill nếu cần: pkill -f "src/main.py"
```

### Lỗi: LLM API rate limit

- Tự động retry với exponential backoff (xem `src/utils/retry.py`)
- Giảm `FETCH_LIMIT` trong .env
- Kiểm tra quota trên OpenAI dashboard

## Development Workflow

```bash
# 1. Tạo branch feature
git checkout -b feature/xyz

# 2. Code, test local
make test
make lint
make typecheck

# 3. Commit
git add .
git commit -m "feat: add xyz"

# 4. Push & tạo PR
git push origin feature/xyz
# CI sẽ chạy lint, typecheck, tests tự động
```

## CI/CD (Phase 3)

Sau khi setup GitHub Secrets:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `LLM_API_KEY`

Workflow `.github/workflows/scrawlnews.yml` sẽ chạy tự động theo cron.