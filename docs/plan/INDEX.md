# ScrawlNews — Project Plan

Thư mục `docs/plan/` chứa **kế hoạch dự án** đầy đủ: ideas, kiến trúc, cách hoạt động, lộ trình, và các quyết định kỹ thuật.

## Cấu trúc thư mục

```
docs/plan/
├── INDEX.md                  ← Bạn đang ở đây — Tổng quan kế hoạch
├── architecture.md           ← Kiến trúc hệ thống, data model, services, edge cases
├── roadmap.md                ← Lộ trình phát triển 3 giai đoạn + milestones
├── technical-deep-dive.md    ← Phân tích kỹ thuật chi tiết, trade-offs, open questions
├── decisions.md              ← Architecture Decision Records (ADR)
├── ideas.md                  ← Ý tưởng mở rộng, future features
├── testing.md                ← Test strategy, layers, parity
├── setup.md                  ← Setup guide, config, install, run
├── usage.md                  ← Hướng dẫn sử dụng agent
├── implementation-notes.md   ← Ghi chép trong quá trình implement
├── execplan-template.md      ← Template cho execution plan
└── api.yaml                  ← OpenAPI REST API spec
```

## Trật tự đọc đề xuất

1. **INDEX.md** — Tổng quan kế hoạch dự án
2. **architecture.md** — Hiểu kiến trúc tổng quan, data model, services, data flows
3. **roadmap.md** — Biết lộ trình phát triển 3 giai đoạn + milestones
4. **technical-deep-dive.md** — Đào chi tiết kỹ thuật, trade-offs, open questions trước khi code
5. **decisions.md** — Các quyết định kiến trúc đã chốt (ADR)
6. **ideas.md** — Ý tưởng mở rộng, future backlog
7. **setup.md** — Chuẩn bị môi trường local
8. **testing.md** — Chiến lược test
9. **usage.md** — Hướng dẫn chạy agent
10. **implementation-notes.md** — Cập nhật trong quá trình code
11. **execplan-template.md** — Template để viết exec plan mới
12. **api.yaml** — Reference cho API spec (nếu có REST layer)

## Mục tiêu dự án

> **ScrawlNews** là một Agent tự động hóa quy trình thu thập, tóm tắt và phân phối tin tức hàng ngày từ Google News.

### 3 Skills cốt lõi

| Skill | Vai trò | Công nghệ | Output |
|-------|---------|-----------|--------|
| **Scrawler** | Thu thập dữ liệu | Python + RSS + trafilatura / Playwright (fallback) | Raw articles |
| **Synthesizer** | Tóm tắt bằng LLM | OpenAI gpt-4o-mini | Summaries |
| **Messenger** | Gửi Telegram | Telegram Bot API | Newsletter |

### Pipeline

```
Google News (RSS) → Scrawler → Articles → Synthesizer → Summaries → Messenger → Telegram
                              │                    │
                              ▼                    ▼
                         ArticleRepo         SummaryRepo
                         (SQLite)            (SQLite)
```

### Deployment

- **Platform**: GitHub Actions (free, cron support)
- **Schedule**: 08:00, 12:00, 16:00, 21:00 UTC daily
- **Secrets**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `LLM_API_KEY`

---

> **Lưu ý**: Đây là thư mục *Plan* — chứa thiết kế và quyết định. Source code nằm ở `src/` (chưa tạo), tests ở `tests/`.