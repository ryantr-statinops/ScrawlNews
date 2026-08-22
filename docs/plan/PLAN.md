# PLAN — Architecture & Roadmap

Kế hoạch kiến trúc và lộ trình phát triển dự án ScrawlNews.

---

## 1. Tổng quan Dự án

**ScrawlNews** là một AI Agent tự động hóa quy trình: **thu thập → tóm tắt → phân phối** tin tức hàng ngày từ Google News, gửi về Telegram.

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

### Deployment

- **Platform**: GitHub Actions (free, cron support)
- **Schedule**: 08:00, 12:00, 16:00, 21:00 UTC daily
- **Secrets**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `LLM_API_KEY`, `OPENROUTER_API_KEY`

---

## 2. System Architecture

### System Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  Scrawler   │────▶│  Synthesizer │────▶│Messenger│
│  Service    │     │  Service     │     │ Service │
└─────────────┘     └──────────────┘     └─────────┘
       │                    │                  │
       ▼                    ▼                  ▼
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│ ArticleRepo │     │ SummaryRepo  │     │Telegram │
│             │     │              │     │  Bot    │
└─────────────┘     └──────────────┘     └─────────┘
```

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py (Pipeline)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Scrawler    │  │ Synthesizer  │  │   Messenger      │  │
│  │  Service     │  │  Service     │  │   Service        │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                     │            │
│         ▼                 ▼                     ▼            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ArticleRepo   │  │SummaryRepo   │  │TelegramBot       │  │
│  │(SQLite)      │  │(SQLite)      │  │(python-telegram) │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│         │                 │                     │            │
│         └─────────────────┼─────────────────────┘            │
│                           ▼                                  │
│                    ┌──────────────┐                          │
│                    │  Config      │                          │
│                    │  (Pydantic)  │                          │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Data Model

### Data Flows

```
Google News RSS
    │
    ▼
Scrawler.fetch() → List[Article]
    │
    ├─── Save to ArticleRepo (dedup by URL hash)
    │
    ▼
Synthesizer.summarize(articles) → List[Summary]
    │
    ├─── Save to SummaryRepo
    │
    ▼
Messenger.send(summaries) → Telegram Chat
```

### Article Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | TEXT | PK, NOT NULL | SHA256(url)[:16] — deterministic |
| `url` | TEXT | UNIQUE, NOT NULL | Link gốc bài viết |
| `title` | TEXT | NOT NULL | Tiêu đề |
| `source` | TEXT | | Nguồn tin (VD: VnExpress, BBC) |
| `raw_html` | TEXT | | HTML gốc (optional, debug/re-summarize) |
| `content` | TEXT | | Nội dung đã extract & clean |
| `fetched_at` | DATETIME | NOT NULL, DEFAULT NOW() | Thời gian fetch |
| `summarized` | INTEGER | NOT NULL, DEFAULT 0 | 0=chưa, 1=đã tóm tắt |

### Summary Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | TEXT | PK, NOT NULL | UUID v4 |
| `article_id` | TEXT | FK→Article.id, NOT NULL | Tham chiếu Article |
| `summary_text` | TEXT | NOT NULL | Nội dung tóm tắt (Markdown) |
| `model_used` | TEXT | NOT NULL | Model LLM (VD: "gpt-4o-mini") |
| `created_at` | DATETIME | NOT NULL, DEFAULT NOW() | Thời gian tạo |

### Indexes

```sql
CREATE INDEX idx_articles_fetched_at ON articles(fetched_at DESC);
CREATE INDEX idx_articles_summarized ON articles(summarized);
CREATE INDEX idx_summaries_article_id ON summaries(article_id);
```

---

## 4. Service Interfaces

Tất cả services kế thừa `BaseService` và implement `execute()`.

### BaseService (Abstract)

```python
class BaseService(ABC):
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the service logic."""
        pass
```

### ScrawlerService

```python
class ScrawlerService(BaseService):
    async def execute(self, limit: int = 20) -> list[Article]:
        """Fetch latest articles from Google News RSS."""
        pass
    
    async def fetch_rss(self, limit: int) -> list[Article]: ...
    async def extract_content(self, url: str) -> str: ...
    async def fetch_playwright_fallback(self, limit: int) -> list[Article]: ...
```

### SynthesizerService

```python
class SynthesizerService(BaseService):
    async def execute(self, articles: list[Article]) -> list[Summary]:
        """Summarize articles using LLM."""
        pass
    
    def build_prompt(self, articles: list[Article]) -> str: ...
    async def call_llm(self, prompt: str) -> str: ...
    def parse_response(self, response: str, articles: list[Article]) -> list[Summary]: ...
```

### MessengerService

```python
class MessengerService(BaseService):
    async def execute(self, summaries: list[Summary]) -> bool:
        """Send summaries to Telegram."""
        pass
    
    def format_message(self, summaries: list[Summary]) -> str: ...
    def split_message(self, text: str, max_len: int = 4000) -> list[str]: ...
    async def send_messages(self, chat_id: int, messages: list[str]) -> bool: ...
```

---

## 5. Repository Pattern

### ArticleRepository

```python
class ArticleRepository:
    def __init__(self, db_path: str = "data/scrawlnews.db"): ...
    
    def save(self, article: Article) -> bool: ...           # INSERT OR IGNORE
    def get_unsummarized(self, limit: int) -> list[Article]: ...
    def mark_summarized(self, article_id: str): ...
    def exists(self, url: str) -> bool: ...                  # dedup check
    def cleanup_old(self, days: int = 7): ...
```

### SummaryRepository

```python
class SummaryRepository:
    def __init__(self, db_path: str = "data/scrawlnews.db"): ...
    
    def save(self, summary: Summary): ...
    def get_by_article(self, article_id: str) -> Summary | None: ...
    def get_recent(self, days: int = 7) -> list[Summary]: ...
```

---

## 6. Configuration & Execution

### Configuration Flow

```
.env file → Pydantic Settings (config.py) → Injected into Services
```

```python
# src/config.py
class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_chat_id: str
    llm_api_key: str
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    fetch_limit: int = 20
    summary_lang: str = "vi"
    retention_days: int = 7
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Async Execution Model

```python
# main.py
async def main():
    config = load_config()
    pipeline = Pipeline(config)
    await pipeline.run()

# Pipeline.run()
async def run(self):
    # 1. Fetch (I/O bound - network)
    articles = await self.scrawler.execute(limit=config.fetch_limit)
    
    # 2. Save & filter new
    new_articles = self.repo.filter_new(articles)
    
    # 3. Summarize (I/O bound - LLM API) - can batch
    summaries = await self.synthesizer.execute(new_articles)
    
    # 4. Send (I/O bound - Telegram API) - sequential due to rate limit
    await self.messenger.execute(summaries)
    
    # 5. Cleanup
    self.repo.cleanup_old(config.retention_days)
```

---

## 7. Error Handling

### Error Handling Flow

```
┌────────────────────────────────────────────────────────────┐
│                    Pipeline.run()                           │
└────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ Scrawler   │ │Synthesizer │ │ Messenger  │
       └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
             │             │              │
      ┌──────┴──────┐ ┌────┴────┐  ┌─────┴─────┐
      ▼             ▼ ▼         ▼  ▼           ▼
   Success      Retry(3x)   Fallback   Retry(3x)
      │             │         (raw)       │
      │         ┌───┴───┐         │   ┌───┴───┐
      │         ▼       ▼         ▼   ▼       ▼
      │      Success  Fail      Send   Success  Save local
      │         │       │         OK      │       file
      ▼         ▼       ▼         ▼       ▼       ▼
   Continue  Continue  Log &     Continue  Log &   Retry
   to next   to next   continue         next run
   stage     stage     to next
   stage     stage     stage
```

### Edge Cases Handling

| Case | Detection | Handling |
|------|-----------|----------|
| Network timeout | `httpx.TimeoutException` | Retry 3x với exponential backoff (2s, 4s, 8s) |
| HTTP 429/5xx | Response status | Retry với circuit breaker sau 5 failures |
| Empty RSS feed | `len(articles) == 0` | Log warning, skip pipeline, notify admin |
| LLM API error | `openai.APIError` | Fallback: gửi raw titles + URLs |
| LLM rate limit | `openai.RateLimitError` | Queue, wait, retry |
| Telegram 429 | `RetryAfter` exception | Sleep `retry_after` seconds, retry |
| Message > 4096 chars | `len(msg) > 4096` | Split tại `\n\n` boundaries |
| Duplicate article | `ArticleRepo.exists(url)` | Skip (INSERT OR IGNORE) |
| Content extraction fail | `trafilatura` returns None | Skip article, log, continue others |
| Config missing | Pydantic validation error | Exit với clear error message |

---

## 8. Source Code Structure

```
src/
├── __init__.py
├── main.py                 # Entry point, Pipeline class
├── config.py               # Pydantic Settings
├── models/
│   ├── __init__.py
│   ├── article.py          # Article dataclass
│   └── summary.py          # Summary dataclass
├── services/
│   ├── __init__.py
│   ├── base.py             # BaseService abstract class
│   ├── scrawler.py         # ScrawlerService
│   ├── synthesizer.py      # SynthesizerService
│   └── messenger.py        # MessengerService
├── repositories/
│   ├── __init__.py
│   ├── article_repo.py     # ArticleRepository
│   └── summary_repo.py     # SummaryRepository
└── utils/
    ├── __init__.py
    ├── retry.py            # Retry decorators, circuit breaker
    ├── formatter.py        # Message formatting
    └── logging.py          # Structured logging setup
```

---

## 9. Security

- **Secrets**: Chỉ qua env vars, không hardcode
- **API Keys**: Không log, mask trong logs
- **Telegram Token**: Chỉ dùng server-side
- **SQLite**: File permissions 600 trên runner
- **Dependencies**: Pin versions, scan vulnerabilities (`pip-audit`)

---

## 10. Roadmap

### Timeline Overview

| Phase | Thời gian ước tính | Mục tiêu chính | Deliverable |
|-------|-------------------|----------------|-------------|
| **Phase 1** | 1-2 tuần | Core pipeline chạy local | `main.py` chạy được end-to-end |
| **Phase 2** | 1-2 tuần | Production-ready, tested | Code quality, SQLite, tests |
| **Phase 3** | 3-5 ngày | Auto-deploy trên GitHub Actions | Chạy tự động 4 lần/ngày |

---

### Phase 1: Xây dựng Core (Local Development)

**Mục tiêu**: Pipeline `main.py` chạy được từ fetch → summarize → send Telegram.

#### Tasks

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

**Milestone 1**: `python src/main.py` chạy thành công, nhận được newsletter trên Telegram.

---

### Phase 2: Tối ưu & Đóng gói (Production Ready)

**Mục tiêu**: Code sạch, có tests, persistent storage, error handling robust.

#### Tasks

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

**Milestone 2**: `make test` pass, `make lint` pass, pipeline chạy stable local nhiều lần.

---

### Phase 3: Triển khai (Deployment & Automation)

**Mục tiêu**: Chạy tự động trên GitHub Actions theo cron.

#### Tasks

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

**Milestone 3**: GitHub Actions chạy tự động 4 lần/ngày, newsletter đến Telegram đúng giờ.

---

### Phase 4+: Mở rộng (Post-MVP)

| Feature | Effort | Priority |
|---------|--------|----------|
| Interactive Telegram Bot | Medium | High |
| Category Filtering | Low | High |
| Multi-source (HN, Reddit) | Medium | Medium |
| Web Dashboard | High | Medium |
| Cost Tracking | Low | Medium |
| Audio Newsletter (TTS) | Medium | Low |

---

## 11. Environment Variables

| Variable | Required | Default | Mô tả |
|----------|----------|---------|-------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Token từ @BotFather |
| `TELEGRAM_CHAT_ID` | ✅ | - | Chat ID cá nhân hoặc channel |
| `LLM_API_KEY` | ✅ | - | API key cho OpenAI |
| `LLM_PROVIDER` | ❌ | `openai` | Provider name |
| `LLM_MODEL` | ❌ | `gpt-4o-mini` | Model name |
| `FETCH_LIMIT` | ❌ | `20` | Max articles per run |
| `SUMMARY_LANG` | ❌ | `vi` | Output language |
| `RETENTION_DAYS` | ❌ | `7` | Data retention |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

---

## 12. Dependencies (requirements.txt draft)

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