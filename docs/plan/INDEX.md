# ScrawlNews — Project Plan Index

Tổng quan nhanh dự án, hướng dẫn đọc tài liệu, và đường dẫn tra cứu nhanh.

---

## 🎯 Project Overview

**ScrawlNews** là một **AI Agent tự động hóa** quy trình: **thu thập → tóm tắt → phân phối** tin tức hàng ngày từ Google News, gửi về Telegram.

### 3 Skills chính

| Skill | Vai trò | Công nghệ | Output |
|-------|--------|-----------|--------|
| **Scrawler** | Thu thập dữ liệu | Python + RSS (feedparser) + HTML extractors (Trafilatura/Readability/Newspaper) | Danh sách articles |
| **Synthesizer** | Tóm tắt bằng LLM | OpenAI / OpenRouter / 9router | Tóm tắt ngắn gọn |
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

Thư mục `docs/plan/` là **kế hoạch dự án** được tổ chức thành các file chuyên đề. Đọc theo trật tự sau:

### 1. Hiểu dự án (đọc trước khi làm gì)
- **INDEX.md** → Bạn đang ở đây — tổng quan + reading guide
- **PLAN.md** → Kiến trúc, data model, roadmap, lộ trình
- **DECISIONS.md** → Các quyết định kỹ thuật đã chốt (8 ADRs)

### 2. Trước khi code
- **IMPLEMENT.md** → Chi tiết technical deep dive, setup, testing, usage
- **IDEAS.md** → Ý tưởng mở rộng, future backlog

### 3. Workflow & ghi chép
- **implementation-notes.md** → Ghi chép implement thực tế
- **execplan-template.md** → Template để viết kế hoạch task mới
- **api.yaml** → OpenAPI spec

---

## 🔍 Đường dẫn tra cứu nhanh

| Bạn cần tìm | File | Section |
|-------------|------|---------|
| Cách Google News scraping hoạt động | IMPLEMENT.md | Section 1: Scrawler |
| Prompt LLM summarization | IMPLEMENT.md | Section 2: Synthesizer |
| Cách Telegram message được format | IMPLEMENT.md | Section 3: Messenger |
| Schema SQLite (articles, summaries) | PLAN.md | Data Model |
| Cách deduplicate articles | PLAN.md | Edge Cases |
| Error handling strategy | IMPLEMENT.md | Section 5: Error Handling |
| GitHub Actions workflow | IMPLEMENT.md | Section 6: GitHub Actions |
| Cấu trúc thư mục src/ | IMPLEMENT.md | Section 10: Dependencies (structure) |
| Test mocking strategies | IMPLEMENT.md | Section 7: Testing Strategy |
| Cách setup môi trường | IMPLEMENT.md | Section 8: Setup Guide |
| Env vars cần thiết | PLAN.md | Environment Variables |
| CLI args | IMPLEMENT.md | Section 9: Usage Guide |
| Debug tips | IMPLEMENT.md | Section 9: Monitoring & Troubleshooting |
| Tại sao chọn RSS | DECISIONS.md | ADR-001 |
| Tại sao chọn gpt-4o-mini | DECISIONS.md | ADR-002 |
| Tất cả trade-offs | DECISIONS.md | All ADRs |
| Open questions | IMPLEMENT.md | Section 11: Open Questions |
| Ý tưởng mở rộng | IDEAS.md | Future Backlog |
| Technical debt | IDEAS.md | Technical Debt Tracker |
| Template exec plan | execplan-template.md | Full file |
| OpenAPI spec | api.yaml | Full file |
| Service interfaces | PLAN.md | Service Interfaces |
| Async execution model | PLAN.md | Async Execution Model |
| Pipeline orchestration | IMPLEMENT.md | Section 4: Pipeline Orchestration |

---

## 📋 Quick References

### Environment Variables

| Variable | Bắt buộc | Default | Mô tả |
|----------|----------|---------|-------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Token từ @BotFather |
| `TELEGRAM_CHAT_ID` | ✅ | - | Chat ID cá nhân hoặc channel |
| `LLM_API_KEY` | ✅ | - | API key cho OpenAI |
| `OPENROUTER_API_KEY` | ❌ | - | API key cho OpenRouter (dùng nếu chọn provider OpenRouter/9router) |
| `LLM_PROVIDER` | ❌ | `openai` | Provider name |
| `LLM_MODEL` | ❌ | `gpt-4o-mini` | Model name |
| `FETCH_LIMIT` | ❌ | `20` | Max articles per run |
| `SUMMARY_LANG` | ❌ | `vi` | Output language |
| `RETENTION_DAYS` | ❌ | `7` | Data retention |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

### GitHub Secrets (cho Actions)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `LLM_API_KEY`
- `OPENROUTER_API_KEY`

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
pydantic, python-dotenv, httpx, tenacity, sqlalchemy
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

Chi tiết trong `PLAN.md`

---

## 📂 Cấu trúc thư mục dự án

```
ScrawlNews/
├── docs/
│   └── plan/                  ← Kế hoạch (bạn đang ở đây)
│       ├── INDEX.md           ← Tổng quan + reading guide
│       ├── PLAN.md            ← Architecture + roadmap
│       ├── IMPLEMENT.md       ← Technical guide + testing + setup + usage
│       ├── DECISIONS.md       ← Architecture decision records (ADRs)
│       ├── IDEAS.md           ← Future backlog + technical debt
│       ├── implementation-notes.md
│       ├── execplan-template.md
│       └── spec/
│           └── api.yaml       ← OpenAPI spec (sắp tạo)
├── src/                       ← Chưa tạo (sẽ có khi code)
├── tests/                     ← Chưa tạo
├── data/                      ← Chưa tạo
├── logs/                      ← Chưa tạo
├── .env.example               ← Chưa tạo
├── requirements.txt           ← Chưa tạo
├── Makefile                   ← Chưa tạo
├── .gitignore
└── README.md
```

---

> 📂 **Lưu ý**: `docs/plan/` là **kế hoạch/thiết kế**. Source code nằm ở `src/` (chưa tạo). Mỗi file trong `docs/plan/` đều độc lập nhưng có liên kết qua cross-references. Sử dụng bảng tra cứu trên để tìm nhanh thông tin.

> ⚠️ **Workflow**: Mỗi khi bắt đầu task mới, dùng `execplan-template.md` để viết kế hoạch → implement → ghi chép vào `implementation-notes.md`.

> 🔗 **Cross-reference**: `PLAN.md` và `IMPLEMENT.md` có nhiều nội dung liên quan. Khi đọc một section, hãy kiểm tra xem có reference đến file khác không.