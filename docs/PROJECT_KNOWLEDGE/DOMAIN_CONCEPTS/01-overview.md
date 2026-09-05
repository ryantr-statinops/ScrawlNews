# 01 — Overview

> Tổng quan dự án, mục đích và luồng tổng thể. Concept cốt lõi, không phụ thuộc tech stack.

## Purpose

ScrawlNews là **Local Monitor Dashboard** cho tin tức. Dashboard là service chính chạy local trong một terminal; newsbot (thu thập, tóm tắt, gửi Telegram) là một feature toggle.

## 3 Services chính (Messenger là feature)

| Service | Vai trò | Công nghệ | Output |
|---------|--------|-----------|--------|
| **Scrawler** | Thu thập dữ liệu | Python + RSS (feedparser) + HTML extractors (Trafilatura/Readability/Newspaper) | Danh sách articles |
| **Synthesizer** | Tóm tắt bằng LLM | OpenAI / OpenRouter / OmniRoute | Tóm tắt ngắn gọn |
| **Messenger** | Gửi thông báo (feature) | Telegram Bot API — `telegram_enabled` toggle | Newsletter (optional) |

## Core Flow

```
Google News RSS -> Scrawler -> Articles -> Synthesizer -> Summaries -> Messenger (optional) -> Telegram
                       |                        |
                       v                        v
                  ArticleRepo              SummaryRepo
                       ^                        ^
                       +---- Dashboard (FastAPI + React) -- Celery/Redis ----+
                                Nginx :80 -> /api :8000, / :5173
```

## Principles

- Dashboard-first: mọi thao tác quan sát và điều khiển qua dashboard
- Pure local: SQLite file mount `./data:/app/data`, không phụ thuộc service ngoài
- Hot-reload hạn chế: chỉ 4 biến đơn giản qua `PUT /api/config`

## Trạng thái hiện tại

Xem [CURRENT_STATE.md](../CURRENT_STATE.md) để biết chi tiết đã build được gì (Stage 1–4 DONE).

## References

- [02-core-engine.md](02-core-engine.md) — logic Scrawler / Synthesizer / Messenger
- [03-interface.md](03-interface.md) — Dashboard API + Web, CLI
- [04-data-config.md](04-data-config.md) — storage, config, hot-reload
- [DECISIONS.md](../DECISIONS.md) — ADR-001/002/006/007
