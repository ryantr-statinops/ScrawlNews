# ScrawlNews — Project Plan Index

Tổng quan nhanh dự án, hướng dẫn đọc tài liệu, và đường dẫn tra cứu nhanh.

---

## 🎯 Project Overview

**ScrawlNews** là một **AI Agent tự động hóa** quy trình: **thu thập → tóm tắt → phân phối** tin tức hàng ngày từ Google News, gửi về Telegram.

### 3 Skills chính

| Skill | Vai trò | Công nghệ | Output |
|-------|--------|-----------|--------|
| **Scrawler** | Thu thập dữ liệu | Python + RSS (feedparser) + trafilatura | Danh sách articles |
| **Synthesizer** | Tóm tắt bằng LLM | OpenAI gpt-4o-mini | Tóm tắt ngắn gọn |
| **Messenger** | Gửi thông báo | Telegram Bot API | Newsletter trên Telegram |

### Pipeline

```
Google News RSS → Scrawler → Articles → Synthesizer → Summaries → Messenger → Telegram
                     │                      │
                     ▼                      ▼
                ArticleRepo            SummaryRepo
                (SQLite)               (SQLite)
```

### Quick Start

```bash
make install
cp .env.example .env
make run
```

---

## 📚 Hướng dẫn đọc tài liệu

Thư mục `docs/plan/` là **kế hoạch dự án** được tổ chức theo vai trò. Đọc theo trật tự sau:

### 1. Getting Started (đọc trước khi làm gì)
- **INDEX.md** → Bạn đang ở đây — tổng quan + reading guide
- **architecture.md** → Hiểu kiến trúc tổng quan, data model, services, edge cases
- **roadmap.md** → Biết lộ trình phát triển 3 giai đoạn + milestones

### 2. Trước khi code
- **technical-deep-dive.md** → Đào chi tiết kỹ thuật, trade-offs, open questions
- **decisions.md** → Các quyết định kiến trúc đã chốt (8 ADRs)

### 3. Tham khảo nhanh trong quá trình code
- **testing.md** → Test strategy, mocking strategies, fixtures
- **setup.md** → Cách setup môi trường, troubleshooting
- **usage.md** → Cách chạy agent, CLI args, FAQ
- **ideas.md** → Ý tưởng mở rộng, technical debt

### 4. Workflow & ghi chú
- **implementation-notes.md** → Ghi chép implement thực tế
- **execplan-template.md** → Template để viết kế hoạch task mới
- **api.yaml** → OpenAPI spec

---

## 🔍 Đường dẫn tra cứu nhanh

| Bạn cần tìm | File | Section |
|-------------|------|---------|
| Cách Google News scraping hoạt động | technical-deep-dive.md | Section 1: Scrawler |
| Prompt LLM summarization | technical-deep-dive.md | Section 2: Synthesizer |
| Cách Telegram message được format | technical-deep-dive.md | Section 3: Messenger |
| Schema SQLite (articles, summaries) | architecture.md | Data Model |
| Cách deduplicate articles | architecture.md | Edge Cases |
| Error handling strategy | technical-deep-dive.md | Section 6: Error Handling |
| GitHub Actions workflow | technical-deep-dive.md | Section 7 |
| Cấu trúc thư mục src/ | technical-deep-dive.md | Section 8 |
| Test mocking strategies | testing.md | Unit Tests section |
| Cách setup môi trường | setup.md | Full file |
| Env vars cần thiết | roadmap.md | Section 3 + setup.md |
| CLI args | usage.md | CLI Modes |
| Debug tips | usage.md | Troubleshooting |
| Tại sao chọn RSS | decisions.md | ADR-001 |
| Tại sao chọn gpt-4o-mini | decisions.md | ADR-002 |
| Tất cả trade-offs | technical-deep-dive.md | Section 10 |
| Open questions | technical-deep-dive.md | Section 11 |
| Ý tưởng mở rộng | ideas.md | Full file |
| Technical debt | ideas.md | Technical Debt Tracker |
| Template exec plan | execplan-template.md | Full file |
| OpenAPI spec | api.yaml | Full file |

---

## 📋 Quick References

### Environment Variables

| Variable | Required | Default | Mô tả |
|----------|----------|---------|-------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Token từ [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ✅ | - | Chat ID cá nhân hoặc channel |
| `LLM_API_KEY` | ✅ | - | API key cho OpenAI |
| `LLM_PROVIDER` | ❌ | `openai` | Provider name |
| `LLM_MODEL` | ❌ | `gpt-4o-mini` | Model name |
| `FETCH_LIMIT` | ❌ | `20` | Max articles per run |
| `SUMMARY_LANG` | ❌ | `vi` | Output language |
| `RETENTION_DAYS` | ❌ | `7` | Data retention days |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

### GitHub Secrets (cho Actions)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `LLM_API_KEY`

### Make Commands
```
make install     ← Cài dependencies
make run         ← Chạy pipeline
make test        ← Chạy tests
make lint        ← Lint code
make format      ← Format code
```

### Dependencies (requirements.txt)
```
feedparser, trafilatura, openai, python-telegram-bot
pydantic, python-dotenv, httpx, tenacity
playwright (optional, fallback scraper)
pytest, pytest-asyncio (dev)
```

---

## 🗺️ Roadmap

| Phase | Mục tiêu | Deliverable | Status |
|-------|----------|-------------|--------|
| **Phase 1** | Core: fetch → summarize → send local | `main.py` chạy được end-to-end | 🟡 Planned |
| **Phase 2** | Production-ready | Tests, lint, SQLite, error handling | 🟡 Planned |
| **Phase 3** | Auto-deploy | GitHub Actions cron workflow | 🟡 Planned |
| **Phase 4+** | Tính năng mở rộng | Interactive bot, categories, dashboard | ⚪ Backlog |

Chi tiết trong `plan/roadmap.md`

---

## 📂 Cấu trúc thư mục dự kiến

```
ScrawlNews/
├── docs/
│   └── plan/                  ← Kế hoạch (bạn đang ở đây)
├── src/
│   ├── main.py                ← Entry point, Pipeline orchestration
│   ├── config.py              ← Pydantic Settings
│   ├── models/                ← Article, Summary dataclasses
│   ├── services/              ← Scrawler, Synthesizer, Messenger
│   ├── repositories/          ← ArticleRepo, SummaryRepo
│   └── utils/                 ← Retry, formatter, logging
├── tests/                     ← Unit + integration tests
├── data/                      ← SQLite DB, raw/processed data
├── logs/                      ← Application logs
├── .env.example
├── requirements.txt
├── Makefile
├── .gitignore
└── README.md
```

---

> 📂 **Lưu ý**: `docs/plan/` là **kế hoạch/thiết kế**. Source code nằm ở `src/` (chưa tạo). Mỗi file trong `docs/plan/` đều độc lập nhưng có liên kết qua references. Sử dụng bảng tra cứu trên để tìm nhanh thông tin.

> ⚠️ **Workflow**: Mỗi khi bắt đầu task mới, dùng `execplan-template.md` để viết kế hoạch → implement → ghi chép vào `implementation-notes.md`.