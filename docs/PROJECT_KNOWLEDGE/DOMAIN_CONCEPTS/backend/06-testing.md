# 06 — Backend Testing

> Pytest strategy, fixtures, mocking, coverage. Cập nhật 2026-09-04.

## Test Pyramid

```
        ┌─────────────┐
        │   E2E       │  ← Few: critical user journeys
        └─────────────┘
        ┌─────────────┐
        │ Integration │  ← Some: service interactions
        └─────────────┘
        ┌─────────────┐
        │   Unit      │  ← Many: individual functions/classes
        └─────────────┘
```

## Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
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
│   ├── test_summary_repo.py
│   ├── test_run_repo.py
│   ├── test_api_articles.py
│   ├── test_api_runs.py
│   ├── test_api_config.py
│   ├── test_api_health.py
│   ├── test_celery_tasks.py
│   └── test_exceptions.py
└── integration/
    ├── test_pipeline.py
    ├── test_database.py
    └── test_api_integration.py
```

## Coverage Goals

| Component | Target |
|-----------|--------|
| Models | 100% |
| Services (core logic) | >90% |
| Repositories | >90% |
| API routes | >90% |
| Utils | >80% |
| Celery tasks | >80% |
| **Overall** | **>85%** |

## Key Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
import tempfile
import sqlite3
from pathlib import Path


@pytest.fixture
def temp_db():
    """Temporary SQLite database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield str(db_path)


@pytest.fixture
def article_repo(temp_db):
    """ArticleRepository with temp DB + migrations."""
    from src.repositories.article_repo import ArticleRepository
    from src.repositories.migrate import run_migrations

    run_migrations(temp_db)
    return ArticleRepository(db_url=f"sqlite:///{temp_db}")


@pytest.fixture
def summary_repo(temp_db):
    from src.repositories.summary_repo import SummaryRepository
    from src.repositories.migrate import run_migrations

    run_migrations(temp_db)
    return SummaryRepository(db_url=f"sqlite:///{temp_db}")


@pytest.fixture
def sample_article():
    """Sample Article instance."""
    from src.models.article import Article
    from datetime import datetime

    return Article(
        id="abc123def456",
        url="https://example.com/article",
        title="Test Article",
        source="TestSource",
        content="Test content",
        fetched_at=datetime(2026, 9, 4, 10, 0, 0),
        summarized=0,
    )


@pytest.fixture
def mock_http_client():
    """Mock httpx.AsyncClient for external API calls."""
    from unittest.mock import AsyncMock, patch

    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    from unittest.mock import patch, AsyncMock

    with patch("openai.AsyncOpenAI") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram Bot."""
    from unittest.mock import patch, AsyncMock

    with patch("telegram.Bot") as mock:
        bot = AsyncMock()
        mock.return_value = bot
        yield bot


@pytest.fixture
def mock_celery_task():
    """Mock Celery task for pipeline.run."""
    from unittest.mock import MagicMock

    task = MagicMock()
    task.request.retries = 0
    task.retry = MagicMock(side_effect=lambda exc, countdown: exc)
    return task
```

## Unit Test Examples

### Test Service (mocked)

```python
# tests/unit/test_scrawler.py
import pytest
from unittest.mock import AsyncMock
from src.services.scrawler import ScrawlerService
from src.services.exceptions import ScrawlerError


class TestScrawlerService:
    @pytest.mark.asyncio
    async def test_fetch_rss_success(self, mock_http_client):
        # Arrange
        mock_http_client.get.return_value.__aenter__.return_value.text = "<rss>...</rss>"

        # Act
        scrawler = ScrawlerService()
        articles = await scrawler.fetch_rss(limit=10)

        # Assert
        assert len(articles) == 10
        assert all(a.url for a in articles)

    @pytest.mark.asyncio
    async def test_network_error_raises_scrawler_error(self, mock_http_client):
        import httpx

        mock_http_client.get.side_effect = httpx.ConnectError("Connection failed")

        scrawler = ScrawlerService()
        with pytest.raises(ScrawlerError):
            await scrawler.execute(limit=10)
```

### Test Repository (real DB)

```python
# tests/unit/test_article_repo.py
import pytest
from src.models.article import Article
from src.services.exceptions import NotFoundError


class TestArticleRepository:
    def test_save_and_get(self, article_repo, sample_article):
        # Act
        article_repo.save(sample_article)
        result = article_repo.get(sample_article.id)

        # Assert
        assert result.url == sample_article.url
        assert result.title == sample_article.title

    def test_dedup_by_url(self, article_repo, sample_article):
        # Act
        article_repo.save(sample_article)
        article_repo.save(sample_article)  # duplicate

        # Assert
        assert article_repo.count() == 1

    def test_get_not_found_raises(self, article_repo):
        with pytest.raises(NotFoundError):
            article_repo.get("nonexistent")

    def test_cleanup_old(self, article_repo, sample_article):
        from datetime import datetime, timedelta
        old_article = Article(
            **sample_article.model_dump(),
            id="old123",
            fetched_at=datetime.utcnow() - timedelta(days=10),
        )
        article_repo.save(old_article)
        article_repo.save(sample_article)

        deleted = article_repo.cleanup_old(days=7)

        assert deleted == 1
        assert article_repo.count() == 1
```

### Test API (with TestClient)

```python
# tests/unit/test_api_articles.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestArticlesAPI:
    def test_list_articles_empty(self, client, article_repo):
        response = client.get("/api/articles")
        assert response.status_code == 200
        assert response.json() == {"count": 0, "articles": []}

    def test_list_articles_with_query(self, client, article_repo, sample_article):
        article_repo.save(sample_article)
        response = client.get("/api/articles?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1

    def test_rate_limit_returns_429(self, client):
        # Make 61 requests in 1 minute
        for _ in range(60):
            client.get("/api/articles")
        response = client.get("/api/articles")
        assert response.status_code == 429
```

### Test Celery Task

```python
# tests/unit/test_celery_tasks.py
import pytest
from unittest.mock import patch, MagicMock
from src.worker.tasks import pipeline_run


class TestPipelineRun:
    def test_pipeline_run_success(self, mock_celery_task, article_repo, summary_repo):
        with patch("src.worker.tasks.ScrawlerService") as mock_scrawler, \
             patch("src.worker.tasks.SynthesizerService") as mock_synth, \
             patch("src.worker.tasks.MessengerService") as mock_msg:

            mock_scrawler.return_value.execute.return_value = []
            mock_synth.return_value.execute.return_value = []
            mock_msg.return_value.execute.return_value = False

            result = pipeline_run.__wrapped__(mock_celery_task)

            assert result["status"] == "success"

    def test_pipeline_run_retries_on_error(self, mock_celery_task):
        from src.services.exceptions import ScrawlError

        with patch("src.worker.tasks.ScrawlerService") as mock_scrawler:
            mock_scrawler.return_value.execute.side_effect = ScrawlError("test")

            with pytest.raises(ScrawlError):
                pipeline_run.__wrapped__(mock_celery_task)

            mock_celery_task.retry.assert_called_once()
```

## Integration Tests

```python
# tests/integration/test_pipeline.py
import pytest
from src.services.scrawler import ScrawlerService
from src.services.synthesizer import SynthesizerService
from src.worker.tasks import pipeline_run


class TestPipelineIntegration:
    @pytest.mark.asyncio
    async def test_full_pipeline_with_mocks(
        self, article_repo, summary_repo, mock_http_client, mock_openai
    ):
        """Test end-to-end with all external calls mocked."""
        # Mock RSS response
        mock_http_client.get.return_value.__aenter__.return_value.text = SAMPLE_RSS

        # Mock LLM response
        mock_openai.chat.completions.create.return_value = mock_llm_response()

        # Run pipeline
        scrawler = ScrawlerService()
        articles = await scrawler.execute(limit=5)

        assert len(articles) > 0
        for a in articles:
            article_repo.save(a)
            assert a.content is not None
```

## CI Integration

```yaml
# .github/workflows/ci.yml
- name: Run BE tests
  run: |
    pytest tests/ --cov=src --cov-report=xml --cov-fail-under=80

- name: Type check BE
  run: mypy src/

- name: Lint BE
  run: ruff check src/
```

## Running Tests

```bash
# All tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Unit only
pytest tests/unit/

# Integration only
pytest tests/integration/

# Specific test
pytest tests/unit/test_scrawler.py::TestScrawlerService::test_fetch_rss_success -v

# With verbose output
pytest tests/ -v --tb=short
```

## Test Data Management

- **Unit tests**: Pure mocks, no external deps, fast (<1s total)
- **Integration tests**: `temp_db` (SQLite tmp), mocked external APIs
- **No real API calls** trong automated tests
- **Fixtures** committed to repo để reproduce

### Sample fixture (sample_articles.json)

```json
[
  {
    "id": "abc123def456",
    "url": "https://example.com/article1",
    "title": "AI Breakthrough in 2024",
    "source": "TechCrunch",
    "content": "Researchers have discovered...",
    "fetched_at": "2026-09-04T10:00:00",
    "summarized": 0
  }
]
```

## References

- [01-stack.md](01-stack.md) — pytest, pytest-asyncio, pytest-cov
- [02-architecture.md](02-architecture.md) — what to test
- [03-patterns.md](03-patterns.md) — exception patterns
