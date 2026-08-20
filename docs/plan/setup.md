# Setup

Hướng dẫn cài đặt và chạy ScrawlNews trên môi trường local.

## Prerequisites

- Python 3.11+
- pip
- (Optional) Playwright browsers nếu dùng scraping mode

## Install

```bash
make install
```

Hoặc thủ công:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuration

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

### Environment Variables

| Variable | Bắt buộc | Mô tả |
|----------|----------|-------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Token từ [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ✅ | Chat ID cá nhân hoặc channel |
| `LLM_API_KEY` | ✅ | API key cho LLM provider |
| `LLM_PROVIDER` | ❌ | Provider mặc định: `openai` |
| `LLM_MODEL` | ❌ | Model mặc định: `gpt-4o-mini` |

## Run

```bash
make run
```

Hoặc:

```bash
python src/main.py
```

## Run Tests

```bash
make test
```

Hoặc:

```bash
pytest tests/
```

## Verify

Chạy dry-run để kiểm tra pipeline không gửi Telegram:

```bash
python src/main.py --dry-run
```
