# Technical Deep Dive

Phân tích chi tiết các thành phần kỹ thuật, thách thức và giải pháp cho ScrawlNews.

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

### Giải pháp đề xuất

#### Option A: Google News RSS Feed (Khuyến nghị)
- URL: `https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en`
- **Ưu điểm**: Không cần Playwright, không bị CAPTCHA, ổn định
- **Nhược điểm**: Chỉ lấy được title + link, không có full content
- **Kết hợp**: Dùng RSS lấy danh sách URLs, rồi dùng `newspaper3k` hoặc `trafilatura` extract full article content từ URL đó

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

#### Option B: Playwright (Phức tạp hơn)
- Cần xử lý:
  - **User-Agent**: Spoof browser UA thật
  - **Headless detection**: Dùng `stealth-plugin` hoặc custom args
  - **Consent popup**: Tìm và click "Accept all" trước khi scrape
  - **Selectors**: Dùng nhiều fallback selectors cho cùng một element
  - **Proxy rotation**: Nếu bị block, rotate qua nhiều IP

```python
from playwright.async_api import async_playwright

async def scrape_google_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
        )
        page = await context.new_page()
        await page.goto("https://news.google.com/topics/...")
        # Handle consent popup if present
        # Extract articles with fallback selectors
```

#### Option C: Third-party API (Trả phí)
- **SerpApi**: Google Search API, có thể lấy Google News results
- **NewsAPI.org**: Chuyên nghiệp, có free tier (100 requests/day)
- **Tavily**: Search API optimized for AI agents

### Khuyến nghị
**Kết hợp A + B**: Dùng RSS cho ổn định, fallback sang Playwright nếu RSS fail. Tránh phụ thuộc hoàn toàn vào scraping.

---

## 2. Synthesizer — Tóm tắt bằng LLM

### Lựa chọn LLM Provider

| Provider | Model | Cost (input/1K tokens) | Context | Khuyến nghị |
|----------|-------|----------------------|---------|-------------|
| OpenAI | gpt-4o-mini | $0.15 / $0.60 | 128K | ✅ Khuyến nghị (rẻ, nhanh, đủ tốt) |
| OpenAI | gpt-4o | $2.50 / $10.00 | 128K | Nếu cần chất lượng cao hơn |
| Anthropic | claude-3-haiku | $0.25 / $1.25 | 200K | Alternative tốt |
| Google | gemini-1.5-flash | $0.075 / $0.30 | 1M | Rẻ nhất, context lớn |
| Local | llama-3.1-8B | Free | 8K | Miễn phí, cần GPU |

### Prompt Engineering cho Summarization

**Chiến lược**: Gom nhiều articles vào 1 prompt để tiết kiệm token và có context tốt hơn.

```python
SYSTEM_PROMPT = """You are a news summarizer. Given a list of news articles, 
create a concise daily briefing in Vietnamese with:
1. Top 3-5 most important stories
2. 1-2 sentences per story explaining what happened
3. Keep it scannable and actionable

Format as Markdown with emojis."""

USER_PROMPT = """Summarize these articles:

{articles_text}

Requirements:
- Language: Vietnamese
- Length: 150-250 words total
- Include source attribution
- Prioritize by relevance to tech/AI/startups"""
```

### Quản lý chi phí

| Scenario | Articles/batch | Tokens/batch | Cost/batch (gpt-4o-mini) |
|----------|---------------|--------------|-------------------------|
| Light | 10 | ~3K | ~$0.0005 |
| Normal | 20 | ~6K | ~$0.001 |
| Heavy | 50 | ~15K | ~$0.003 |

**Chi phí rất thấp** cho mục đích personal use.

### Xử lý lỗi
- Nếu LLM API fail → gửi raw article titles thay vì summaries
- Nếu rate limited → queue và retry sau
- Nếu context quá dài → chunk articles trước khi summarize

---

## 3. Messenger — Gửi qua Telegram

### Setup
1. Tạo bot với [@BotFather](https://t.me/BotFather)
   - Lệnh: `/newbot` → nhận `TELEGRAM_BOT_TOKEN`
2. Lấy Chat ID:
   - Gửi message cho bot → vào `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Hoặc dùng [@getidsbot](https://t.me/getidsbot)

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
    # Split at natural boundaries (double newline)
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

## 4. Data Model & Storage

### SQLite Schema

```sql
-- Articles đã fetch (tránh trùng lặp)
CREATE TABLE articles (
    id TEXT PRIMARY KEY,           -- UUID
    url TEXT UNIQUE NOT NULL,      -- URL gốc
    title TEXT NOT NULL,
    source TEXT,
    raw_html TEXT,                 -- Raw HTML (optional, để re-summarize)
    content TEXT,                  -- Cleaned text content
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    summarized INTEGER DEFAULT 0  -- Flag: đã tóm tắt chưa
);

-- Summaries đã tạo
CREATE TABLE summaries (
    id TEXT PRIMARY KEY,           -- UUID
    article_id TEXT NOT NULL,
    summary_text TEXT NOT NULL,
    model_used TEXT,               -- e.g. "gpt-4o-mini"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- Index để query nhanh
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_fetched_at ON articles(fetched_at);
CREATE INDEX idx_summaries_article_id ON summaries(article_id);
```

### Deduplication Strategy
```python
import hashlib

def article_id(url: str) -> str:
    """Generate deterministic ID from URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]

def is_duplicate(db, url: str) -> bool:
    """Check if article already exists."""
    aid = article_id(url)
    return db.execute("SELECT id FROM articles WHERE id = ?", (aid,)).fetchone() is not None
```

### Retention Policy
```python
# Giữ articles trong 7 ngày, sau đó xóa
def cleanup_old_articles(db):
    db.execute("DELETE FROM articles WHERE fetched_at < datetime('now', '-7 days')")
    db.execute("DELETE FROM summaries WHERE article_id NOT IN (SELECT id FROM articles)")
    db.commit()
```

---

## 5. Pipeline Orchestration

### main.py Flow

```
┌─────────────────────────────────────────────┐
│                  main.py                     │
│  (Entry point, dùng argparse hoặc click)     │
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

## 6. Error Handling & Resilience

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

### Circuit Breaker
```python
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # Normal
    OPEN = "open"           # Too many failures, skip calls
    HALF_OPEN = "half_open" # Testing if recovered

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit is open")
        
        try:
            result = await func(*args, **kwargs)
            self.failures = 0
            self.state = CircuitState.CLOSED
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
            raise
```

### Graceful Degradation
| Component fails | Fallback behavior |
|---------------|------------------|
| Scrawler fails | Log error, exit (nothing to summarize) |
| Synthesizer fails | Send raw article titles + URLs |
| Messenger fails | Save to local file, retry next run |
| LLM timeout | Skip that article, summarize others |

---

## 7. GitHub Actions Deployment

### Workflow Structure

```yaml
# .github/workflows/scrawlnews.yml
name: ScrawlNews Daily

on:
  schedule:
    - cron: '0 8,12,16,21 * * *'  # 8h, 12h, 16h, 21h UTC
  workflow_dispatch:  # Cho phép trigger manual

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
        run: python main.py
```

### Secrets cần cấu hình
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `LLM_API_KEY`

---

## 8. Cấu trúc file đề xuất

```
ScrawlNews/
├── .github/
│   └── workflows/
│       └── scrawlnews.yml
├── config/
│   ├── __init__.py
│   └── settings.py          # Pydantic settings, load từ .env
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point, argparse
│   ├── models/
│   │   ├── __init__.py
│   │   ├── article.py       # Article dataclass
│   │   └── summary.py       # Summary dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scrawler.py      # Google News fetching
│   │   ├── synthesizer.py   # LLM summarization
│   │   └── messenger.py     # Telegram delivery
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── article_repo.py  # SQLite CRUD
│   └── utils/
│       ├── __init__.py
│       ├── retry.py         # Exponential backoff
│       └── formatter.py     # Message formatting
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_scrawler.py
│   │   ├── test_synthesizer.py
│   │   └── test_messenger.py
│   └── integration/
│       └── test_pipeline.py
├── data/
│   ├── raw/                 # Raw HTML backup (optional)
│   └── processed/           # Summaries output
├── logs/                    # Application logs
├── requirements.txt
├── Makefile
├── .env.example
├── .gitignore
└── README.md
```

---

## 9. Dependencies đề xuất

```
# requirements.txt
playwright>=1.40.0          # Scrawler (fallback scraping)
trafilatura>=1.6.0          # Article extraction (primary)
feedparser>=6.0.10          # RSS parsing
openai>=1.0.0               # LLM client
python-dotenv>=1.0.0        # Config management
pydantic>=2.0.0             # Data validation
httpx>=0.25.0               # Async HTTP client
tenacity>=8.2.0             # Retry logic
python-telegram-bot>=20.0   # Telegram Bot API
sqlalchemy>=2.0.0           # ORM (optional, hoặc dùng sqlite3 trực tiếp)
pytest>=7.4.0               # Testing
pytest-asyncio>=0.21.0      # Async test support
```

---

## 10. Trade-offs & Decisions cần chốt

| Decision | Options | Khuyến nghị | Lý do |
|----------|---------|-------------|--------|
| **Cách fetch Google News** | RSS / Playwright / API | **RSS + trafilatura** | Ổn định, free, không cần browser |
| **LLM Provider** | OpenAI / Anthropic / Google / Local | **OpenAI gpt-4o-mini** | Rẻ, nhanh, đủ tốt cho summarization |
| **Database** | SQLite / PostgreSQL / None | **SQLite** | Đủ cho personal use, không cần server |
| **Sync vs Async** | Sync / Async | **Async** | I/O bound (network calls), async hiệu quả hơn |
| **Orchestration** | Script / Airflow / Prefect | **Script đơn giản** | Đủ cho 4 runs/ngày, không cần over-engineering |
| **Deployment** | GitHub Actions / VPS / Lambda | **GitHub Actions** | Free, tích hợp sẵn secrets, cron job |

---

## 11. Open Questions cần trả lời trước khi code

1. **Ngôn ngữ output**: Newsletter bằng tiếng Việt hay tiếng Anh?
2. **Chủ đề**: Có filter theo category (tech, business, world) hay lấy tất cả?
3. **Số lượng articles**: Mỗi lần fetch bao nhiêu? (10, 20, 50?)
4. **LLM fallback**: Nếu API fail, có gửi raw titles không?
5. **Interactive mode**: Cần cho phase 1 hay postpone?
6. **Deduplication**: So khớp URL hash hay title similarity?
7. **News source**: Chỉ Google News hay thêm các nguồn khác?
