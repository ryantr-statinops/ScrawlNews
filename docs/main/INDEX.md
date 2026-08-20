# Documentation — Index

Thư mục `docs/main/` chứa toàn bộ tài liệu dự án ScrawlNews, được tổ chức theo chức năng thay vì theo phase.

## Cấu trúc thư mục

```
docs/main/
├── INDEX.md                  ← Bạn đang ở đây
├── architecture.md           ← Kiến trúc hệ thống, data model, services, edge cases
├── roadmap.md                ← Lộ trình phát triển 3 giai đoạn
├── technical-deep-dive.md    ← Phân tích kỹ thuật chi tiết, trade-offs, open questions
├── testing.md                ← Test strategy, layers, parity
├── setup.md                  ← Setup guide, config, install, run
├── usage.md                  ← Hướng dẫn sử dụng agent
├── implementation-notes.md   ← Ghi chép trong quá trình implement
├── execplan-template.md      ← Template cho execution plan
└── api.yaml                  ← OpenAPI REST API spec
```

## Trật tự đọc đề xuất

1. **INDEX.md** — Tổng quan cấu trúc tài liệu
2. **architecture.md** — Hiểu kiến trúc tổng quan, data model, services, data flows
3. **roadmap.md** — Biết lộ trình phát triển 3 giai đoạn
4. **technical-deep-dive.md** — Đào chi tiết kỹ thuật, trade-offs, open questions trước khi code
5. **setup.md** — Chuẩn bị môi trường local
6. **testing.md** — Chiến lược test
7. **usage.md** — Hướng dẫn chạy agent
8. **implementation-notes.md** — Cập nhật trong quá trình code
9. **execplan-template.md** — Template để viết exec plan mới
10. **api.yaml** — Reference cho API spec (nếu có REST layer)

## Mô tả từng file

| File | Nội dung | Nguồn |
|------|----------|--------|
| `architecture.md` | System diagram, data model (Article, Summary), services (Scrawler, Synthesizer, Messenger), repos, data flows, edge cases | phase2 overview + phase3 design |
| `roadmap.md` | 3 giai đoạn: Core, Optimize, Deploy. Env vars. Bonus features | phase1 execplan |
| `technical-deep-dive.md` | Google News scraping challenges, LLM provider comparison, Telegram formatting, SQLite schema, pipeline orchestration, error handling, GitHub Actions, file structure, dependencies, trade-offs, open questions | phase1 technical deep dive |
| `testing.md` | Unit tests cho models + 3 services. Integration tests cho pipeline + E2E. Parity strategy | phase3 validation |
| `setup.md` | Install dependencies, config env vars, run agent, run tests | phase5 how_to_use_agent + phase1 config section |
| `usage.md` | Cách sử dụng agent hàng ngày | phase5 how_to_use_agent |
| `implementation-notes.md` | Ghi chép trong quá trình implement | phase4 implementation notes |
| `execplan-template.md` | Template markdown cho execution plan | phase5 template |
| `api.yaml` | OpenAPI 3.0.3 spec: /api/fetch, /api/summarize, /health, schemas | phase3 spec |
