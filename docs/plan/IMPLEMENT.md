# IMPLEMENT — Technical Implementation Guide

Chi tiết kỹ thuật, testing, setup, và cách sử dụng ScrawlNews. Xem [PLAN.md](PLAN.md) trước để hiểu kiến trúc tổng quan.

---

## 1. Scrawler — Thu thập dữ liệu từ Google News

### Vấn đề chính
Google News **không có public API miễn phí**. Việc scrape trực tiếp gặp nhiều khó khăn:

| Thách thức | Mô tả | Mức độ ảnh hưởng |
|-----------|-------|-----------------|
| Anti-bot | Google phát hiện headless browser, CAPTCHA, block IP | Cao |
| Cấu trúc thay đổi | CSS selectors, HTML structure thay đổi thường xuyên | Cao |
| GDPR consent | Popup đồng ý cookie xuất hiện ở EU regions | Trung bình |
| Dynamic content | Nội dung load bằng JavaScript, cần browser thực | Trung bình |
| Rate limiting | Quá nhiều request → 429 hoặc tạm block | Trung bình |

### Data Source Options

#### Option A: Google News RSS Feed (Khuyến nghị)
- URL: `https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en`
- **Ưu điểm**: Không cần Playwright, không bị CAPTCHA, ổn định
- **Nhược điểm**: Chỉ lấy được title + link, không có full content
- **Kết hợp**: Dùng RSS lấy danh sách URLs, rồi dùng `trafilatura` extract full article content từ URL đó

```python
import feedparser
import trafilatura

# Step 1: Lấy URLs từ RSS
feed = feedparser.parse("https://news.google.com/rss/search?q=AI&hl=en-US")
urls = [entry.link for entry in feed.entries[:10]]

# Step 2: Extract full content
for url in urls:
    downloaded = trafilatura.fetch_url(url)
    content = trafilatura.extract(downloaded)
```

#### Option B: Playwright (Fallback)
- Cần xử lý: User-Agent spoofing, headless detection bypass, consent popup, fallback selectors
- Chỉ dùng khi RSS fail

#### Option C: Third-party API (Trả phí)
- SerpApi, NewsAPI.org, Tavily

### Khuyến nghị
Dùng RSS + trafilatura làm primary, Playwright làm fallback. Xem thêm chi tiết trong `decisions.md` ADR-001.

---

## 2. Synthesizer — Tóm tắt bằng LLM

### Lựa chọn LLM Provider

| Provider | Model | Cost (input/1K tokens) | Context | Khuyến nghị |
|----------|-------|----------------------|---------|-------------|
| OpenAI | gpt-4o-mini | $0.15 / $0.60 | 128K | ✅ Khuyến nghị |
| OpenAI | gpt-4o | $2.50 / $10.00 | 128K | Chất lượng cao hơn |
| Anthropic | claude-3-haiku | $0.25 / $1.25 | 200K | Alternative tốt |
| Google | gemini-1.5-flash | $0.075 / $0.30 | 1M | Rẻ nhất |
| Local | llama-3.1-8B | Free | 8K | Cần GPU |

Xem chi tiết lựa chọn trong `decisions.md` ADR-002.

### Prompt Engineering cho Summarization

**Chiến lược**: Gom nhiều articles vào 1 prompt để tiết kiệm token.

```python
SYSTEM_PROMPT = """You are a news summarizer. Given a list of news articles, 
create a concise daily briefing in Vietnamese with:
1. Top 3-5 most important stories
2. 1-2 sentences per story explaining what happened
3. Keep it scannable and actionable
"""

USER_PROMPT = """Summarize these articles:

{articles_text}

Requirements:
- Language: Vietnamese
- Length: 150-250 words total
- Include source attribution
- Prioritize by relevance to tech/AI/startups"""
```

### Chi phí ước tính

| Scenario | Articles/batch | Tokens/batch | Cost (gpt-4o-mini) |
|----------|---------------|--------------|-------------------| 
| Light | 10 | ~3K | ~$0.0005 |
| Normal | 20 | ~6K | ~$0.001 |
| Heavy | 50 | ~15K | ~$0.003 |

---

## 3. Messenger — Gửi qua Telegram

### Message Formatting

**Telegram limits**:
- Max 4096 characters per message
- Max 1 message/second per chat

```python
def format_newsletter(summaries: list[dict]) -> str:
    lines = ["📰 **Daily News Briefing**\n"]
    for s in summaries:
        lines.append(f"• **{s['title']}**")
        lines.append(f"  {s['summary']}")
        lines.append(f"  [Đọc thêm]({s['url']})\n")
    return "\n".join(lines)

# Split long messages
def split_message(text: str, max_len: int = 4000) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts = text.split("\n\n")
    messages, current = [], ""
    for part in parts:
        if len(current) + len(part) + 2 <= max_len:
            current += part + "\n\n"
        else:
            messages.append(current.strip())
            current = part + "\n\n"
    if current:
        messages.append(current.strip())
    return messages
```

### Rate Limiting
```python
import asyncio

async def send_telegram_messages(bot, chat_id, messages):
    for msg in messages:
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
        await asyncio.sleep(1)  # 1 message/second limit
```

---

## 4. Pipeline Orchestration

### main.py Flow

```
┌─────────────────────────────────────────────┐
│                  main.py                     │
│  (Entry point, dùng argparse)               │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │Scrawler │ │Synthesizer│ │Messenger│
   └─────────┘ └─────────┘ └─────────┘
        │           │           │
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │Article  │ │Summary  │ │Telegram │
   │Repo     │ │Repo     │ │Bot      │
   └─────────┘ └─────────┘ └─────────┘
```

### Orchestration Code Skeleton

```python
import asyncio
from pathlib import Path
from datetime import datetime

class Pipeline:
    def __init__(self, config: dict):
        self.config = config
        self.scrawler = Scrawler(config)
        self.synthesizer = Synthesizer(config)
        self.messenger = Messenger(config)
        self.repo = ArticleRepository("data/scrawlnews.db")
    
    async def run(self):
        start = datetime.now()
        print(f"[{start}] Starting pipeline...")
        
        # Step 1: Fetch articles
        try:
            raw_articles = await self.scrawler.fetch()
            print(f"Fetched {len(raw_articles)} articles")
        except Exception as e:
            print(f"Scrawler failed: {e}")
            return
        
        # Step 2: Save & deduplicate
        saved = []
        for article in raw_articles:
            if not self.repo.is_duplicate(article.url):
                self.repo.save(article)
                saved.append(article)
        
        if not saved:
            print("No new articles to summarize")
            return
        
        # Step 3: Summarize
        try:
            summaries = await self.synthesizer.summarize(saved)
            self.repo.save_summaries(summaries)
            print(f"Generated {len(summaries)} summaries")
        except Exception as e:
            print(f"Synthesizer failed: {e}")
            # Fallback: send raw titles
            summaries = [{"title": a.title, "url": a.url} for a in saved]
        
        # Step 4: Send to Telegram
        try:
            await self.messenger.send(summaries)
            print("Sent to Telegram")
        except Exception as e:
            print(f"Messenger failed: {e}")
        
        # Step 5: Cleanup
        self.repo.cleanup_old(days=7)
        
        end = datetime.now()
        print(f"[{end}] Pipeline completed in {(end-start).total_seconds():.1f}s")

if __name__ == "__main__":
    config = load_config()
    pipeline = Pipeline(config)
    asyncio.run(pipeline.run())
```

---

## 5. Error Handling & Resilience

(Chi tiết tại [PLAN.md](PLAN.md) Section 6-7 và [DECISIONS.md](DECISIONS.md) ADR-008)

### Retry Strategy (Exponential Backoff)

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
)
async def fetch_with_retry(url: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text
```

### Graceful Degradation
| Component fails | Fallback behavior |
|---------------|------------------|
| Scrawler fails | Log error, exit |
| Synthesizer fails | Send raw article titles + URLs |
| Messenger fails | Save to local file, retry next run |
| LLM timeout | Skip that article, summarize others |

---

## 6. GitHub Actions Deployment

### Workflow Structure

```yaml
# .github/workflows/scrawlnews.yml
name: ScrawlNews Daily

on:
  schedule:
    - cron: '0 8,12,16,21 * * *'  # 8h, 12h, 16h, 21h UTC
  workflow_dispatch:

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      - name: Run pipeline
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        run: python src/main.py
```

### Secrets cần cấu hình
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `LLM_API_KEY`

---

## 7. Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │   E2E       │  ← Few: Critical user journeys
        └─────────────┘
        ┌─────────────┐
        │ Integration │  ← Some: Service interactions
        └─────────────┘
        ┌─────────────┐
        │   Unit      │  ← Many: Individual functions/classes
        └─────────────┘
```

### Test Structure

```
tests/
├── conftest.py
├── fixtures/
│   ├── sample_articles.json
│   ├── sample_rss.xml
│   ├── sample_html.html
│   └── llm_responses.json
├── unit/
│   ├── test_models.py
│   ├── test_config.py
│   ├── test_scrawler.py
│   ├── test_synthesizer.py
│   ├── test_messenger.py
│   ├── test_article_repo.py
│   └── test_summary_repo.py
└── integration/
    ├── test_pipeline.py
    └── test_database.py
```

### Test Plan

| Layer | Type | File | Coverage Target |
|-------|------|------|-----------------|
| Models | Unit | `tests/unit/test_models.py` | 100% |
| Config | Unit | `tests/unit/test_config.py` | 100% |
| Scrawler | Unit | `tests/unit/test_scrawler.py` | >90% |
| Synthesizer | Unit | `tests/unit/test_synthesizer.py` | >90% |
| Messenger | Unit | `tests/unit/test_messenger.py` | >90% |
| ArticleRepo | Unit | `tests/unit/test_article_repo.py` | >90% |
| SummaryRepo | Unit | `tests/unit/test_summary_repo.py` | >90% |
| Pipeline | Integration | `tests/integration/test_pipeline.py` | Critical paths |
| Database | Integration | `tests/integration/test_database.py` | >80% |

> **Note**: Original plan had `test_fetch_summarize_flow.py` (renamed to `test_pipeline.py`) and `test_end_to_end.py` (renamed to `test_database.py`). If E2E testing is needed, add `tests/integration/test_e2e.py`.

### Parity Strategy

If a legacy system exists, `tests/parity/test_parity.py` compares outputs giữa old và new implementation để đảm bảo tính nhất quán.

### Key Mocking Strategies

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx
from dataclasses import asdict

@pytest.fixture
def mock_http_client():
    """Mock httpx.AsyncClient for external API calls."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client

@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with patch("openai.AsyncOpenAI") as mock:
        yield mock.return_value

@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram Bot."""
    with patch("telegram.Bot") as mock:
        bot = AsyncMock()
        mock.return_value = bot
        yield bot

@pytest.fixture
def sample_articles():
    """Load sample articles from fixture."""
    with open("tests/fixtures/sample_articles.json") as f:
        return [Article(**a) for a in json.load(f)]

@pytest.fixture
def temp_db(tmp_path):
    """Temporary SQLite database for testing."""
    db_path = tmp_path / "test.db"
    yield db_path
    # cleanup handled by tmp_path
```

### Unit Test Examples

```python
# tests/unit/test_scrawler.py
class TestScrawlerService:
    @pytest.mark.asyncio
    async def test_fetch_rss_success(self, mock_http_client, sample_rss_xml):
        mock_http_client.get.return_value = mock_response(text=sample_rss_xml)
        
        articles = await scrawler.fetch_rss(limit=10)
        
        assert len(articles) == 10
        assert all(isinstance(a, Article) for a in articles)
        assert all(a.url for a in articles)

    @pytest.mark.asyncio
    async def test_extract_content_success(self, mock_http_client, sample_html):
        mock_http_client.get.return_value = mock_response(text=sample_html)
        
        content = await scrawler.extract_content("https://example.com/article")
        assert "expected content" in content

    @pytest.mark.asyncio
    async def test_fetch_rss_empty(self, mock_http_client):
        mock_http_client.get.return_value = mock_response(
            text="<rss><channel><item/></channel></rss>")
        
        articles = await scrawler.fetch_rss(limit=10)
        assert articles == []

    @pytest.mark.asyncio
    async def test_fetch_rss_network_error(self, mock_http_client):
        mock_http_client.get.side_effect = httpx.ConnectError("Connection failed")
        
        with pytest.raises(ScrawlerError):
            await scrawler.fetch_rss(limit=10)

# tests/unit/test_synthesizer.py
class TestSynthesizerService:
    @pytest.mark.asyncio
    async def test_summarize_batch(self, mock_openai, sample_articles):
        mock_openai.chat.completions.create.return_value = mock_llm_response()
        
        summaries = await synthesizer.execute(sample_articles)
        
        assert len(summaries) == len(sample_articles)
        assert all(s.summary_text for s in summaries)
        mock_openai.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_summarize_empty_list(self):
        summaries = await synthesizer.execute([])
        assert summaries == []

    @pytest.mark.asyncio
    async def test_llm_error_fallback(self, mock_openai, sample_articles):
        mock_openai.chat.completions.create.side_effect = openai.APIError("Rate limit")
        
        # Should fallback to raw titles
        summaries = await synthesizer.execute(sample_articles)
        assert len(summaries) == len(sample_articles)

# tests/unit/test_messenger.py
class TestMessengerService:
    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_telegram_bot, sample_summaries):
        mock_telegram_bot.send_message.return_value = MagicMock()
        
        result = await messenger.execute(sample_summaries)
        assert result is True
        assert mock_telegram_bot.send_message.call_count >= 1

    @pytest.mark.asyncio
    async def test_message_splitting(self):
        long_text = "x" * 5000
        parts = messenger.split_message(long_text, max_len=4000)
        assert len(parts) == 2
        assert all(len(p) <= 4000 for p in parts)

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, mock_telegram_bot):
        from telegram.error import RetryAfter
        mock_telegram_bot.send_message.side_effect = [
            RetryAfter(retry_after=2),
            MagicMock()  # Second call succeeds
        ]
        
        result = await messenger.execute([sample_summary])
        assert result is True

# tests/unit/test_article_repo.py
class TestArticleRepository:
    def test_save_and_get(self, temp_db):
        repo = ArticleRepository(str(temp_db))
        article = Article(id="abc123", url="https://example.com", title="Test")
        
        repo.save(article)
        retrieved = repo.get_by_id("abc123")
        assert retrieved.url == "https://example.com"

    def test_dedup_by_url(self, temp_db):
        repo = ArticleRepository(str(temp_db))
        article = Article(id="abc123", url="https://example.com", title="Test")
        
        repo.save(article)
        repo.save(article)  # Same URL
        
        count = repo.count()
        assert count == 1

    def test_cleanup_old(self, temp_db):
        repo = ArticleRepository(str(temp_db))
        # Add old and new articles
        repo.cleanup_old(days=7)
        # Verify old removed, new kept
```

### Integration Test Example

```python
# tests/integration/test_pipeline.py
class TestPipeline:
    @pytest.mark.asyncio
    async def test_full_pipeline_dry_run(self, temp_db, mock_all_external):
        """Test pipeline end-to-end with all external calls mocked."""
        pipeline = Pipeline(config=test_config(db_path=temp_db))
        
        result = await pipeline.run(dry_run=True)
        
        assert result.success is True
        assert result.articles_fetched > 0
        assert result.summaries_generated > 0
        # No Telegram calls in dry-run

    @pytest.mark.asyncio
    async def test_pipeline_skip_summarized(self, temp_db, mock_all_external):
        """Articles already summarized should be skipped."""
        # Pre-populate DB with summarized articles
        # Run pipeline
        # Verify only new articles processed
```

### Test Data Management

- **Unit tests**: Pure mocks, no external deps, fast (<1s total)
- **Integration tests**: In-memory SQLite (`:memory:` or `tmp_path`), mocked external APIs
- **No real API calls** in automated tests
- **Fixtures** committed to repo for reproducibility

**Fixture files**:
- `tests/fixtures/sample_articles.json` — Sample Article data
- `tests/fixtures/sample_rss.xml` — Sample Google News RSS response
- `tests/fixtures/sample_html.html` — Sample article HTML for extraction tests
- `tests/fixtures/llm_responses.json` — Mock LLM response payloads

```json
// sample_articles.json
[
  {
    "id": "abc123",
    "url": "https://example.com/article1",
    "title": "AI Breakthrough in 2024",
    "source": "TechCrunch",
    "content": "Researchers have discovered...",
    "fetched_at": "2024-01-15T10:00:00",
    "summarized": 0
  }
]
```

### CI Integration

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: |
    pytest tests/ --cov=src --cov-fail-under=80
- name: Type check
  run: mypy src/
- name: Lint
  run: ruff check src/
```

### Coverage Goals

| Component | Target |
|-----------|--------|
| Models | 100% |
| Services (core logic) | >90% |
| Repositories | >90% |
| Utils | >80% |
| Overall | >85% |

### Running Tests

```bash
# All tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Unit only
pytest tests/unit/

# Integration only
pytest tests/integration/

# Specific test
pytest tests/unit/test_scrawler.py::TestScrawlerService::test_fetch_rss_success -v
```

---

## 8. Setup Guide

### Prerequisites
- Python 3.11+
- pip
- Git

### Quick Start

```bash
# 1. Clone
git clone https://github.com/ryantr-statinops/ScrawlNews.git
cd ScrawlNews

# 2. Install
make install
# Hoặc manual:
# python -m venv .venv && source .venv/bin/activate
# pip install -r requirements.txt
# playwright install chromium

# 3. Config
cp .env.example .env
# Edit .env với credentials

# 4. Test
make test

# 5. Run
make run
# Hoặc: python src/main.py
```

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
| `RETENTION_DAYS` | ❌ | `7` | Data retention |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

### Make Commands

| Command | Mô tả |
|---------|-------|
| `make install` | Cài dependencies, Playwright |
| `make run` | Chạy pipeline |
| `make test` | Chạy tests |
| `make lint` | Ruff lint + format check |
| `make format` | Format code |
| `make typecheck` | MyPy type checking |
| `make clean` | Xóa cache, data, logs |

### Project Structure

```
ScrawlNews/
├── .env                    # Local config (không commit)
├── .env.example            # Template config
├── Makefile                # Commands: install, run, test, lint
├── requirements.txt        # Python dependencies
├── src/
│   ├── __init__.py
│   ├── main.py             # Entry point, Pipeline class
│   ├── config.py           # Pydantic Settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── article.py      # Article dataclass
│   │   └── summary.py      # Summary dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base.py         # BaseService abstract class
│   │   ├── scrawler.py     # ScrawlerService
│   │   ├── synthesizer.py  # SynthesizerService
│   │   └── messenger.py    # MessengerService
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── article_repo.py # ArticleRepository
│   │   └── summary_repo.py # SummaryRepository
│   └── utils/
│       ├── __init__.py
│       ├── retry.py        # Retry decorators, circuit breaker
│       ├── formatter.py    # Message formatting
│       └── logging.py      # Structured logging setup
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Shared fixtures
│   ├── fixtures/           # Sample data
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── data/                   # SQLite DB, raw/processed data
├── logs/                   # Application logs
├── .gitignore
└── README.md
```

### Development Workflow

```bash
# 1. Tạo feature branch
git checkout -b feature/xyz

# 2. Code, test local
make test
make lint
make typecheck

# 3. Commit
git add .
git commit -m "feat: add xyz"

# 4. Push & tạo PR
git push origin feature/xyz
# CI sẽ chạy lint, typecheck, tests tự động
```

### Troubleshooting

**ModuleNotFoundError: No module named 'src'**
→ Chạy từ root directory của project

**TELEGRAM_BOT_TOKEN not set**
→ Kiểm tra `.env` file, đảm bảo không có spaces quanh dấu `=`

**Playwright browser not found**
→ Chạy `playwright install chromium`

**SQLite "database is locked"**
→ Chỉ chạy 1 instance. Kill bằng `pkill -f "src/main.py"`

**LLM API rate limit**
→ Tự động retry. Giảm `FETCH_LIMIT` trong `.env`

**Telegram fail**
→ Pipeline sẽ save newsletter to local file, retry next run

**How to get TELEGRAM_CHAT_ID:**
Gửi message cho bot → truy cập `https://api.telegram.org/bot<TOKEN>/getUpdates` → tìm `chat.id`

---

## 9. Usage Guide

### Run Modes

```bash
# Normal run (gửi Telegram)
python src/main.py

# Dry run (log ra console, không gửi Telegram)
python src/main.py --dry-run

# Xem lịch sử
python src/main.py --history

# Verbose logging
LOG_LEVEL=DEBUG python src/main.py

# Override env vars
FETCH_LIMIT=10 SUMMARY_LANG=en python src/main.py
```

### Newsletter Format

```
📰 **Daily News Briefing** — 2024-01-15 21:00 UTC

🔴 **AI Breakthrough: New Model Beats GPT-4**
Researchers at Stanford developed a new architecture...
[Đọc thêm](https://techcrunch.com/...)

🟢 **Vietnam Tech Startup Raises $50M Series B**
Local fintech company expands to Southeast Asia...
[Đọc thêm](https://vnexpress.net/...)

---
📊 15 articles • 3.2k tokens • $0.0012 • 12.3s
```

- Nếu newsletter > 4096 chars → tự động chia thành multiple messages
- Mỗi message cách nhau 1 giây (Telegram rate limit)

### GitHub Actions Chạy Tự Động

- 08:00 UTC → 15:00 VN
- 12:00 UTC → 19:00 VN
- 16:00 UTC → 23:00 VN
- 21:00 UTC → 04:00 VN (hôm sau)

**Manual trigger**: GitHub → Actions → ScrawlNews Daily → Run workflow

### Monitoring Commands

```bash
# Check database
sqlite3 data/scrawlnews.db "SELECT COUNT(*) FROM articles;"

# Check recent runs
sqlite3 data/scrawlnews.db "
  SELECT fetched_at, COUNT(*) 
  FROM articles 
  GROUP BY date(fetched_at) 
  ORDER BY fetched_at DESC 
  LIMIT 10;
"

# View logs
tail -f logs/scrawlnews.log
```

### Telegram Bot Commands (Future - Phase 4+)

| Command | Mô tả |
|---------|-------|
| `/start` | Welcome message |
| `/latest` | Gửi newsletter mới nhất |
| `/detail <id>` | Chi tiết một bài viết |
| `/topic tech` | Filter theo category |
| `/settings` | Cấu hình preferences |

---

## 10. Dependencies (requirements.txt)

```
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

---

## 11. Open Questions (cần trả lời trước khi code)

1. **Ngôn ngữ output**: Newsletter bằng tiếng Việt hay tiếng Anh? → Quyết định: Tiếng Việt (xem ADR-006)
2. **Chủ đề**: Có filter theo category hay lấy tất cả? → Tạm thời lấy tất cả, filter Phase 4
3. **Số lượng articles**: Mỗi lần fetch bao nhiêu? → Default 20, configurable qua `FETCH_LIMIT`
4. **LLM fallback**: Nếu API fail, có gửi raw titles không? → Có (graceful degradation)
5. **Interactive mode**: Cần cho phase 1 không? → Postpone sang Phase 4
6. **Deduplication**: URL hash hay title similarity? → SHA256(URL)[:16] (xem ADR-007)

Xem thêm chi tiết trong `decisions.md`.

---

> 🔄 **Cross-reference**: For high-level architecture and timeline, go back to [PLAN.md](PLAN.md). For technical decisions, see [DECISIONS.md](DECISIONS.md).