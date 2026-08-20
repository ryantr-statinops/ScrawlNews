# Roadmap

Lộ trình phát triển ScrawlNews theo 3 giai đoạn với milestones rõ ràng.

## Tổng quan Timeline

| Phase | Thời gian ước tính | Mục tiêu chính | Deliverable |
|-------|-------------------|----------------|-------------|
| **Phase 1** | 1-2 tuần | Core pipeline chạy local | `main.py` chạy được end-to-end |
| **Phase 2** | 1-2 tuần | Production-ready, tested | Code quality, SQLite, tests |
| **Phase 3** | 3-5 ngày | Auto-deploy trên GitHub Actions | Chạy tự động 4 lần/ngày |

---

## Phase 1: Xây dựng Core (Local Development)

**Mục tiêu**: Pipeline `main.py` chạy được từ fetch → summarize → send Telegram.

### Tasks

- [ ] **1.1 Project Setup**
  - [ ] Tạo `requirements.txt` với dependencies
  - [ ] Tạo `Makefile` (install, run, test, lint)
  - [ ] Tạo `.env.example` với tất cả env vars
  - [ ] Cấu trúc `src/` package: `src/main.py`, `src/config.py`, `src/models/`, `src/services/`, `src/repositories/`, `src/utils/`

- [ ] **1.2 Scrawler Service**
  - [ ] Implement RSS fetch từ Google News (`feedparser`)
  - [ ] Implement content extraction (`trafilatura`)
  - [ ] Fallback Playwright scraper (optional, Phase 2)
  - [ ] Output: list of `Article` dataclass

- [ ] **1.3 Synthesizer Service**
  - [ ] OpenAI client wrapper (async)
  - [ ] Prompt template cho summarization
  - [ ] Batch processing multiple articles
  - [ ] Structured output parsing (JSON)
  - [ ] Fallback: raw titles nếu LLM fail

- [ ] **1.4 Messenger Service**
  - [ ] Telegram Bot client (`python-telegram-bot`)
  - [ ] Message formatting (MarkdownV2)
  - [ ] Message splitting (>4096 chars)
  - [ ] Rate limiting (1 msg/sec)

- [ ] **1.5 Pipeline Orchestration**
  - [ ] `Pipeline` class trong `src/main.py`
  - [ ] CLI args: `--dry-run`, `--history`, `--help`
  - [ ] Logging setup
  - [ ] End-to-end test local

### Milestone 1 ✅
> `python src/main.py` chạy thành công, nhận được newsletter trên Telegram.

---

## Phase 2: Tối ưu & Đóng gói (Production Ready)

**Mục tiêu**: Code sạch, có tests, persistent storage, error handling robust.

### Tasks

- [ ] **2.1 Configuration System**
  - [ ] Pydantic Settings (`src/config.py`)
  - [ ] Validation env vars
  - [ ] Defaults hợp lý

- [ ] **2.2 SQLite Persistence**
  - [ ] `ArticleRepository` + `SummaryRepository`
  - [ ] Schema migration (simple version table)
  - [ ] Dedup by URL hash
  - [ ] Cleanup job (retention 7 ngày)

- [ ] **2.3 Error Handling & Resilience**
  - [ ] Retry với exponential backoff (`tenacity`)
  - [ ] Circuit breaker cho LLM API
  - [ ] Graceful degradation (xem ADR-008)
  - [ ] Structured logging (JSON, levels)

- [ ] **2.4 Testing**
  - [ ] Unit tests: models, scrawler, synthesizer, messenger
  - [ ] Integration test: pipeline flow với mocks
  - [ ] Fixtures cho sample articles
  - [ ] Coverage target: >80%

- [ ] **2.5 Code Quality**
  - [ ] Ruff (lint + format)
  - [ ] MyPy (type checking)
  - [ ] Pre-commit hooks
  - [ ] Docstrings cho public APIs

### Milestone 2 ✅
> `make test` pass, `make lint` pass, pipeline chạy stable local nhiều lần.

---

## Phase 3: Triển khai (Deployment & Automation)

**Mục tiêu**: Chạy tự động trên GitHub Actions theo cron.

### Tasks

- [ ] **3.1 GitHub Actions Workflow**
  - [ ] `.github/workflows/scrawlnews.yml`
  - [ ] Setup Python, install deps, Playwright browsers
  - [ ] Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `LLM_API_KEY`
  - [ ] Cron: `0 8,12,16,21 * * *` (UTC)
  - [ ] `workflow_dispatch` cho manual trigger

- [ ] **3.2 CI Pipeline**
  - [ ] Lint + typecheck trên PR
  - [ ] Unit + integration tests trên PR
  - [ ] Build check

- [ ] **3.3 Verification**
  - [ ] Test run trên GitHub Actions (manual trigger)
  - [ ] Kiểm tra logs, artifacts
  - [ ] Verify newsletter nhận được trên Telegram
  - [ ] Monitor 2-3 runs tự động

### Milestone 3 ✅
> GitHub Actions chạy tự động 4 lần/ngày, newsletter đến Telegram đúng giờ.

---

## Phase 4+: Mở rộng (Post-MVP)

| Feature | Effort | Priority |
|---------|--------|----------|
| Interactive Telegram Bot | Medium | High |
| Category Filtering | Low | High |
| Multi-source (HN, Reddit) | Medium | Medium |
| Web Dashboard | High | Medium |
| Cost Tracking | Low | Medium |
| Audio Newsletter (TTS) | Medium | Low |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | BotFather token |
| `TELEGRAM_CHAT_ID` | ✅ | - | Target chat/channel |
| `LLM_API_KEY` | ✅ | - | OpenAI API key |
| `LLM_PROVIDER` | ❌ | `openai` | Provider name |
| `LLM_MODEL` | ❌ | `gpt-4o-mini` | Model name |
| `FETCH_LIMIT` | ❌ | `20` | Max articles per run |
| `SUMMARY_LANG` | ❌ | `vi` | Output language |
| `RETENTION_DAYS` | ❌ | `7` | Data retention |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

---

## Dependencies (requirements.txt draft)

```txt
# Core
feedparser>=6.0.10
trafilatura>=1.6.0
openai>=1.0.0
python-telegram-bot>=20.0
pydantic>=2.0.0
python-dotenv>=1.0.0
httpx>=0.25.0
tenacity>=8.2.0
sqlalchemy>=2.0.0

# Optional: Playwright fallback
playwright>=1.40.0

# Dev
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
ruff>=0.4.0
mypy>=1.10.0
pre-commit>=3.6.0
```