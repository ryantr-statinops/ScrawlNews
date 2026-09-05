# ScrawlNews — Documentation

Tài liệu dự án được chia thành 2 phần chính:

- **PROJECT_KNOWLEDGE** — Hiểu dự án là gì, đang ở đâu, muốn thành gì, và tại sao.
- **EXECUTION** — Kế hoạch, task, thứ đã xong, và thứ đã lưu trữ.

## Quick links

- 🚀 **[QUICKSTART.md](PROJECT_KNOWLEDGE/QUICKSTART.md)** — Chạy project trong 5 phút
- ❓ **[FAQ.md](PROJECT_KNOWLEDGE/FAQ.md)** — Câu hỏi thường gặp
- 📖 **[GLOSSARY.md](PROJECT_KNOWLEDGE/GLOSSARY.md)** — Bảng chú giải thuật ngữ
- 📋 **[DOCS_ROADMAP.md](PROJECT_KNOWLEDGE/DOCS_ROADMAP.md)** — Kế hoạch soạn docs

## Đọc từ đâu?

| Bạn muốn biết… | Đọc file |
|---|---|
| Dự án đang thực sự như thế nào (đã build được gì) | [PROJECT_KNOWLEDGE/CURRENT_STATE.md](PROJECT_KNOWLEDGE/CURRENT_STATE.md) |
| Dự án muốn trở thành như thế nào (kiến trúc đích) | [PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md](PROJECT_KNOWLEDGE/TARGET_ARCHITECTURE.md) |
| Tại sao team/AI quyết định xây như vậy (ADR) | [PROJECT_KNOWLEDGE/DECISIONS.md](PROJECT_KNOWLEDGE/DECISIONS.md) |
| Dự án nói về cái gì (domain concepts) | [PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/](PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/) |
| Backend stack + patterns | [PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/backend/](PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/backend/) |
| Frontend stack + patterns | [PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/](PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/) |
| Pipeline + data flow + performance | [PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/pipeline/](PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/pipeline/) |
| Kế hoạch đang thực hiện (roadmap, spec) | [EXECUTION/ACTIVE_PLANS/](EXECUTION/ACTIVE_PLANS/) |
| Task cần làm / đang làm | [EXECUTION/TASKS/](EXECUTION/TASKS/) |
| Những gì đã hoàn thành (developer log) | [EXECUTION/COMPLETED/](EXECUTION/COMPLETED/) |
| Plan/task cũ không còn active (tham khảo) | [EXECUTION/ARCHIVED/](EXECUTION/ARCHIVED/) |
| Cách setup / test / deploy | [GUIDES/](GUIDES/) |

## Cấu trúc

```
docs/
├── README.md                         ← Bạn đang ở đây
├── PROJECT_KNOWLEDGE/
│   ├── QUICKSTART.md                 ← 5 phút setup
│   ├── FAQ.md                        ← Câu hỏi thường gặp
│   ├── GLOSSARY.md                   ← Thuật ngữ
│   ├── DOCS_ROADMAP.md               ← Kế hoạch soạn docs
│   ├── CURRENT_STATE.md              ← Project đang thực sự như thế nào
│   ├── TARGET_ARCHITECTURE.md        ← Project muốn trở thành như thế nào
│   ├── DECISIONS.md                  ← Tại sao quyết định xây như vậy (ADR)
│   └── DOMAIN_CONCEPTS/
│       ├── 01-overview.md            ← Mục đích, luồng tổng thể
│       ├── 02-core-engine.md         ← Scrawler / Synthesizer / Messenger
│       ├── 03-interface.md           ← Dashboard (API + Web) / CLI
│       ├── 04-data-config.md         ← Storage, config, hot-reload
│       ├── 05-extensibility.md       ← Security, skill system
│       ├── backend/                  ← Backend stack, architecture, patterns, ...
│       ├── frontend/                 ← Frontend stack, design tokens, ...
│       └── pipeline/                 ← Pipeline sequence, data model, performance
├── EXECUTION/
│   ├── ACTIVE_PLANS/
│   │   ├── roadmap.md                ← Kế hoạch đang thực hiện (stages)
│   │   ├── execplan-template.md      ← Template viết plan mới
│   │   └── specs/
│   │       └── api.yaml              ← OpenAPI spec (active contract)
│   ├── TASKS/
│   │   ├── TODO.md                   ← Những đơn vị công việc cần làm
│   │   └── IN_PROGRESS.md            ← Task đang thực hiện
│   ├── COMPLETED/
│   │   ├── changelog.md              ← Đã hoàn thành (developer log)
│   │   └── reports/                  ← Test reports, verification results
│   └── ARCHIVED/
│       ├── old-plans.md              ← Plans cũ, superseded
│       ├── ideas.md                  ← Ý tưởng tương lai (backlog)
│       └── obsolete-specs/           ← API specs cũ (tham khảo)
└── GUIDES/
    ├── setup.md                      ← Dev setup, config, troubleshooting
    ├── testing.md                    ← Testing strategy
    └── deployment.md                 ← Deploy (GitHub Actions, Docker, Nginx)
```

> Nguyên tắc: `PROJECT_KNOWLEDGE` giải thích **tại sao / là gì**, `EXECUTION` giải thích **làm gì / đã làm gì**, `GUIDES` giải thích **làm sao**.
