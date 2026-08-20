# Testing

Chiến lược test cho ScrawlNews.

## Test Pyramid

```
        ┌─────────────┐
        │   E2E       │  ← Few: Critical user journeys
        │  (Manual)   │
        ├─────────────┤
        │ Integration │  ← Some: Service interactions
        ├─────────────┤
        │   Unit      │  ← Many: Individual functions/classes
        └─────────────┘
```

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures, pytest config
├── fixtures/
│   ├── sample_articles.json    # Sample Article data
│   ├── sample_rss.xml          # Sample Google News RSS
│   ├── sample_html.html        # Sample article HTML
│   └── llm_responses.json      # Mock LLM responses
├── unit/
│   ├── test_models.py          # Article, Summary dataclasses
│   ├── test_config.py          # Settings validation
│   ├── test_scrawler.py        # ScrawlerService
│   ├── test_synthesizer.py     # SynthesizerService
│   ├── test_messenger.py       # MessengerService
│   ├── test_article_repo.py    # ArticleRepository
│   └── test_summary_repo.py    # SummaryRepository
└── integration/
    ├── test_pipeline.py        # Full pipeline flow
    └── test_database.py        # SQLite operations
```

## Test Plan

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

## Unit Test Guidelines

### Mocking Strategy

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx

@pytest.fixture
def mock_httpx_client():
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

### Scrawler Tests

```python
# tests/unit/test_scrawler.py
class TestScrawlerService:
    @pytest.mark.asyncio
    async def test_fetch_rss_success(self, mock_httpx_client, sample_rss_xml):
        mock_httpx_client.get.return_value = mock_response(text=sample_rss_xml)
        
        articles = await scrawler.fetch_rss(limit=10)
        
        assert len(articles) == 10
        assert all(isinstance(a, Article) for a in articles)
        assert all(a.url for a in articles)

    @pytest.mark.asyncio
    async def test_extract_content_success(self, mock_httpx_client, sample_html):
        mock_httpx_client.get.return_value = mock_response(text=sample_html)
        
        content = await scrawler.extract_content("https://example.com/article")
        
        assert "expected content" in content

    @pytest.mark.asyncio
    async def test_fetch_rss_empty(self, mock_httpx_client):
        mock_httpx_client.get.return_value = mock_response(text="<rss><channel><item/></channel></rss>")
        
        articles = await scrawler.fetch_rss(limit=10)
        
        assert articles == []

    @pytest.mark.asyncio
    async def test_fetch_rss_network_error(self, mock_httpx_client):
        mock_httpx_client.get.side_effect = httpx.ConnectError("Connection failed")
        
        with pytest.raises(ScrawlerError):
            await scrawler.fetch_rss(limit=10)
```

### Synthesizer Tests

```python
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
        assert all("raw" in s.summary_text.lower() or s.summary_text == a.title for s, a in zip(summaries, sample_articles))
```

### Messenger Tests

```python
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
        assert mock_telegram_bot.send_message.call_count == 2
```

### Repository Tests

```python
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

## Integration Tests

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

## Fixtures

### tests/fixtures/sample_articles.json
```json
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

### tests/fixtures/sample_rss.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Google News - Technology</title>
    <item>
      <title>AI Breakthrough in 2024</title>
      <link>https://example.com/article1</link>
      <source>TechCrunch</source>
      <pubDate>Mon, 15 Jan 2024 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
```

## Running Tests

```bash
# All tests
make test
# hoặc
pytest tests/

# Unit only
make test-unit
# hoặc
pytest tests/unit/

# Integration only
make test-int
# hoặc
pytest tests/integration/

# With coverage
pytest tests/ --cov=src --cov-report=term-missing

# Verbose
pytest tests/ -v

# Specific test
pytest tests/unit/test_scrawler.py::TestScrawlerService::test_fetch_rss_success -v
```

## CI Integration

```yaml
# .github/workflows/ci.yml (Phase 2)
- name: Run tests
  run: |
    pytest tests/ --cov=src --cov-fail-under=80
- name: Type check
  run: mypy src/
- name: Lint
  run: ruff check src/
```

## Coverage Goals

| Component | Target |
|-----------|--------|
| Models | 100% |
| Services (core logic) | >90% |
| Repositories | >90% |
| Utils | >80% |
| Overall | >85% |

## Test Data Management

- **Unit tests**: Pure mocks, no external deps, fast (<1s total)
- **Integration tests**: In-memory SQLite (`:memory:` or tmp_path), mocked external APIs
- **No real API calls** in automated tests
- **Fixtures** committed to repo for reproducibility