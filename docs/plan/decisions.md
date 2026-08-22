# Architecture Decision Records (ADR)

Ghi nhận các quyết định kiến trúc quan trọng đã chốt.

## ADR-001: Google News Data Source — RSS + trafilatura

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần lấy tin tức từ Google News. Google không cung cấp public API miễn phí.

### Options
1. **RSS Feed + trafilatura** — Google News có RSS feed công khai, trafilatura extract full content từ URL
2. **Playwright Scraping** — Crawl trực tiếp HTML, xử lý anti-bot, consent popup
3. **Third-party API** (SerpApi, NewsAPI, Tavily) — Trả phí, có rate limit

### Decision
Chọn **Option 1 (RSS + trafilatura)** làm primary.
**Fallback chain**: Nếu trafilatura fail → thử Readability-lxml → cuối cùng là Playwright (Option 2).

### Rationale
- RSS ổn định, không bị CAPTCHA, không cần browser
- trafilatura extract content tốt, xử lý được hầu hết news sites (F1=0.909)
- Readability-lxml làm fallback trung gian (F1=0.801), đơn giản, không cần network request phức tạp
- Playwright chỉ dùng khi cả hai thư viện trên fail (ví dụ: cấu trúc RSS thay đổi, site cần JS render)
- Chi phí = 0 (free)

### Consequences
- Không lấy được full content trực tiếp từ RSS (chỉ title + link + snippet)
- Cần request riêng từng URL để extract content → chậm hơn
- Phụ thuộc vào trafilatura maintainability

---

## ADR-002: LLM Provider — OpenAI gpt-4o-mini

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần LLM để tóm tắt tin tức. Cân bằng giữa chất lượng, chi phí, tốc độ.

### Options
| Model | Cost/1K tokens (in/out) | Context | Quality |
|-------|------------------------|---------|---------|
| gpt-4o-mini | $0.15 / $0.60 | 128K | Tốt |
| gpt-4o | $2.50 / $10.00 | 128K | Rất tốt |
| claude-3-haiku | $0.25 / $1.25 | 200K | Tốt |
| gemini-1.5-flash | $0.075 / $0.30 | 1M | Tốt |
| Local (llama-3.1-8B) | Free (GPU) | 8K | Trung bình |

### Decision
Chọn **OpenAI gpt-4o-mini** làm default, config được qua `LLM_MODEL` env var.

### Rationale
- Chi phí rất thấp (~$0.001/batch 20 articles)
- Chất lượng đủ tốt cho summarization
- API ổn định, SDK mature
- Dễ switch sang model khác qua config

---

## ADR-003: Storage — SQLite

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần lưu articles, summaries để dedup, history, re-summarize.

### Options
1. **SQLite** — File-based, zero-config, đủ cho single-user
2. **PostgreSQL** — Production-grade, cần server
3. **JSON files** — Simple, nhưng query khó
4. **In-memory** — Mất data khi restart

### Decision
Chọn **SQLite** với schema: `articles` + `summaries` tables.

### Rationale
- Zero setup, phù hợp GitHub Actions runner
- ACID, query linh hoạt
- Dễ backup (chỉ copy file)
- Đủ cho personal use (thousands of records)

---

## ADR-004: Orchestration — Single Python Script

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần chạy pipeline: fetch → summarize → send.

### Options
1. **Single script (`main.py`)** — Simple, trực quan
2. **Workflow engine** (Airflow, Prefect, Dagster) — Overkill
3. **Makefile + shell** — Khó debug, error handling yếu

### Decision
Chọn **single async Python script** (`src/main.py`) với class `Pipeline`.

### Rationale
- Dễ hiểu, dễ debug, dễ test
- Async I/O hiệu quả cho network calls
- Không cần dependency ngoài stdlib + requirements
- GitHub Actions chạy được trực tiếp

---

## ADR-005: Deployment — GitHub Actions

**Date**: 2025-08-21
**Status**: Accepted

### Context
Cần chạy tự động 4 lần/ngày.

### Options
1. **GitHub Actions** — Free, integrated, cron support
2. **VPS + cron** — Tốn tiền, maintain server
3. **AWS Lambda / Cloud Functions** — Setup phức tạp
4. **Render / Fly.io** — Có free tier nhưng giới hạn

### Decision
Chọn **GitHub Actions** với cron `0 8,12,16,21 * * *`.

### Rationale
- Free cho public repo, 2000 min/tháng cho private
- Secrets management built-in
- Logs, artifacts, re-run UI
- Playwright chạy được trên ubuntu-latest runner

---

## ADR-006: Language — Vietnamese Output

**Date**: 2025-08-21
**Status**: Accepted

### Context
Newsletter gửi về Telegram, ngôn ngữ nào?

### Decision
**Tiếng Việt** cho newsletter content. Code/comments/docs bằng tiếng Anh (chuẩn dev).

### Rationale
- User là tiếng Việt
- LLM hỗ trợ tốt tiếng Việt
- Code tiếng Anh dễ maintain, share, hire

---

## ADR-007: Deduplication — URL SHA256 Hash

**Date**: 2025-08-21
**Status**: Accepted

### Context
Tránh gửi trùng tin tức đã fetch trước đó.

### Decision
Dùng `SHA256(url)[:16]` làm `article_id` (primary key).

### Rationale
- Deterministic: cùng URL → cùng ID
- Không cần central ID generator
- 16 hex chars = 64 bits → collision probability gần 0
- Simple, no external deps

---

## ADR-008: Error Handling — Graceful Degradation

**Date**: 2025-08-21
**Status**: Accepted

### Context
Pipeline không được "chết" khi một component fail.

### Decision
| Component fail | Fallback |
|---------------|----------|
| Scrawler | Log error, exit (nothing to process) |
| Synthesizer (LLM) | Gửi raw article titles + URLs |
| Messenger (Telegram) | Save to local file, retry next run |
| Individual article extract | Skip article, continue others |

### Rationale
- Partial success > total failure
- User vẫn nhận được thông tin (raw titles) khi LLM fail
- Telegram fail không làm mất data (có local backup)

---

## ADR-009: LLM Provider — OpenRouter / 9router Options

**Date**: 2025-08-22
**Status**: Accepted

### Context
Cần LLM để tóm tắt tin tức. OpenAI gpt-4o-mini trả phí ($0.15/1K tokens). Có nhiều free/cheaper alternatives.

### Options
| Option | Setup | Cost | Multi-model | Complexity |
|--------|-------|------|-------------|------------|
| **A: OpenRouter API** | Chỉ cần API key | Free - $0.15/1K | Manual switch | Thấp |
| **B: 9router** | Cài Node.js + chạy server local | Free (auto route) | Auto-fallback | Trung bình |
| **C: Direct OpenAI** | API key trực tiếp | $0.15/1K | Manual switch | Thấp |

### Decision
- **Phase 1**: Dùng **Option A (OpenRouter)** làm default — đơn giản, không cần server.
- **Phase 2+**: Có thể chuyển sang **Option B (9router)** nếu cần auto-fallback giữa nhiều providers.

### Rationale
- OpenRouter có nhiều free models (`google/gemma-2-9b-it`, `meta/llama-3-8b-instruct`)
- 9router cung cấp auto-fallback + RTK token compression (tiết kiệm 20-40% tokens)
- Giữ `LLM_API_KEY` env var để backward compatible với OpenAI direct
- Thêm `OPENROUTER_API_KEY` cho OpenRouter/9router

### Consequences
- Cần quản lý 2 API keys (`LLM_API_KEY` + `OPENROUTER_API_KEY`)
- Config phải support switch provider qua `LLM_PROVIDER` env var
- 9router cần Node.js runtime trên GitHub Actions runner