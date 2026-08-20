# Architecture

Kiến trúc hệ thống ScrawlNews: Skill-based Agent pipeline.

## System Diagram

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

## High-Level Component Diagram

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

## Skills

| Skill | Role | Module | Technology | Status |
|-------|------|--------|-----------|--------|
| **Scrawler** | Collector | `src/services/scrawler.py` | Python + RSS (feedparser) + trafilatura / Playwright (fallback) | Planned |
| **Synthesizer** | Summary Wrapper | `src/services/synthesizer.py` | OpenAI gpt-4o-mini (configurable) | Planned |
| **Messenger** | Notifier | `src/services/messenger.py` | Telegram Bot API (python-telegram-bot) | Planned |

## Data Flows

### Primary Flow (RSS + trafilatura)
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

### Fallback Flow (Playwright)
```
Google News HTML (Playwright)
    │
    ▼
Scrawler.fetch_fallback() → List[Article]
    │ (same as primary)
```

## Data Model

### Article
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | TEXT | PK, NOT NULL | SHA256(url)[:16] — deterministic |
| `url` | TEXT | UNIQUE, NOT NULL | Link gốc bài viết |
| `title` | TEXT | NOT NULL | Tiêu đề |
| `source` | TEXT | | Nguồn tin (VD: VnExpress, BBC) |
| `raw_html` | TEXT | | HTML gốc (optional, debug/re-summarize) |
| `content` | TEXT | | Nội dung đã extract & clean |
| `fetched_at` | DATETIME | NOT NULL, DEFAULT NOW() | Thời điểm fetch |
| `summarized` | INTEGER | NOT NULL, DEFAULT 0 | 0=chưa, 1=đã tóm tắt |

### Summary
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | TEXT | PK, NOT NULL | UUID v4 |
| `article_id` | TEXT | FK→Article.id, NOT NULL | Tham chiếu Article |
| `summary_text` | TEXT | NOT NULL | Nội dung tóm tắt (Markdown) |
| `model_used` | TEXT | NOT NULL | Model LLM (VD: "gpt-4o-mini") |
| `created_at` | DATETIME | NOT NULL, DEFAULT NOW() | Thời điểm tạo |

### Indexes
```sql
CREATE INDEX idx_articles_fetched_at ON articles(fetched_at DESC);
CREATE INDEX idx_articles_summarized ON articles(summarized);
CREATE INDEX idx_summaries_article_id ON summaries(article_id);
```

## Service Interfaces

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

## Repository Pattern

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

## Configuration Flow

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

## Async Execution Model

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

## Error Handling Flow

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

## Edge Cases Handling

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

## Directory Structure (src/)

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

## Security Considerations

- **Secrets**: Chỉ qua env vars, không hardcode
- **API Keys**: Không log, mask trong logs
- **Telegram Token**: Chỉ dùng server-side
- **SQLite**: File permissions 600 trên runner
- **Dependencies**: Pin versions, scan vulnerabilities (`pip-audit`)