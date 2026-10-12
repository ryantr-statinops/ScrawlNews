# 03 — Backend Patterns

> BaseService, Repository, error handling, retry, logging. Cập nhật 2026-09-04.

## BaseService (Abstract)

Tất cả services kế thừa `BaseService` và implement `execute()`.

```python
# src/services/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseService(ABC):
    """Abstract base for all services."""

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the service logic."""
        raise NotImplementedError
```

```python
# src/services/scrawler.py
from src.services.base import BaseService
from src.services.exceptions import ScrawlerError

class ScrawlerService(BaseService):
    async def execute(self, limit: int = 20) -> list[Article]:
        try:
            articles = await self.fetch_rss(limit)
            return articles
        except httpx.HTTPError as e:
            raise ScrawlerError(f"Failed to fetch RSS: {e}") from e

    async def fetch_rss(self, limit: int) -> list[Article]: ...
    async def extract_content(self, url: str) -> str: ...
```

## Custom Exception Hierarchy

```python
# src/services/exceptions.py
class ScrawlError(Exception):
    """Base for all ScrawlNews errors."""
    def __init__(self, message: str = "ScrawlNews error") -> None:
        self.message = message
        super().__init__(message)

# Service-level
class ScrawlerError(ScrawlError): ...
class SynthesizerError(ScrawlError): ...
class MessengerError(ScrawlError): ...

# Repository-level
class RepositoryError(ScrawlError): ...
class NotFoundError(RepositoryError): ...
class DuplicateError(RepositoryError): ...

# Other
class ConfigError(ScrawlError): ...
class PipelineError(ScrawlError): ...
```

### FastAPI Exception Handlers

```python
# src/api/main.py
from fastapi.responses import JSONResponse
from src.services.exceptions import NotFoundError, ScrawlError

@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": exc.message})

@app.exception_handler(ScrawlError)
async def scrawl_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": exc.message})
```

### Celery Task Handling

```python
# src/worker/tasks.py
from celery.utils.log import get_task_logger
from src.services.exceptions import ScrawlError

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def pipeline_run(self):
    try:
        pipeline = Pipeline()
        pipeline.run()
    except ScrawlError as exc:
        logger.exception("pipeline_run failed", exc_info=exc)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

## Repository Pattern

```python
# src/repositories/article_repo.py
import sqlite3
from src.config import settings
from src.models.article import Article
from src.services.exceptions import NotFoundError, RepositoryError

class ArticleRepository:
    def __init__(self, db_url: str | None = None) -> None:
        url = db_url or settings.database_url
        # sqlite:///data/scrawlnews.db → data/scrawlnews.db
        self.db_path = url.replace("sqlite:///", "")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save(self, article: Article) -> bool:
        """INSERT OR IGNORE (dedup by url)."""
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO articles (id, url, title, source, content, fetched_at, summarized) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (article.id, article.url, article.title, article.source, article.content, article.fetched_at, article.summarized),
                )
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to save article: {e}") from e

    def get(self, article_id: str) -> Article:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
            if not row:
                raise NotFoundError(f"Article {article_id} not found")
            return Article(**dict(row))

    def list(self, q: str | None = None, source: str | None = None, limit: int = 20) -> list[Article]:
        with self._connect() as conn:
            sql = "SELECT * FROM articles WHERE 1=1"
            params: list = []
            if q:
                sql += " AND (title LIKE ? OR content LIKE ?)"
                params.extend([f"%{q}%", f"%{q}%"])
            if source:
                sql += " AND source = ?"
                params.append(source)
            sql += " ORDER BY fetched_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
            return [Article(**dict(r)) for r in rows]

    def cleanup_old(self, days: int = 7) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM articles WHERE fetched_at < datetime('now', ?)",
                (f"-{days} days",),
            )
            conn.commit()
            return cur.rowcount
```

## Retry Pattern (tenacity)

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)
async def fetch_with_retry(url: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text
```

## Logging (structlog)

```python
# src/utils/logging.py
import structlog

def configure_logging(level: str = "INFO") -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
    )

# Usage
from src.utils.logging import get_logger
logger = get_logger(__name__)

logger.info("article_fetched", url=article.url, source=article.source)
logger.error("llm_failed", model=model, error=str(e))
```

Output (JSON):
```json
{"event": "article_fetched", "url": "https://...", "source": "VnExpress", "level": "info", "timestamp": "2026-09-04T10:30:00Z"}
```

## Rate Limit (slowapi)

```python
# src/api/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter

# Per-endpoint override
@router.post("/api/runs")
@limiter.limit("1/30seconds")  # Run Now max 1/30s
def trigger_run(request: Request, fetch_limit: int | None = None): ...
```

## Pydantic Settings

```python
# src/config.py
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite:///data/scrawlnews.db"
    redis_url: str = "redis://localhost:6379/0"
    telegram_enabled: bool = True
    llm_api_key: str
    openrouter_api_key: str | None = None
    fetch_limit: int = 20
    summary_lang: str = "vi"
    retention_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def check_telegram(self):
        if self.telegram_enabled and not self.telegram_bot_token:
            raise ValueError("telegram_enabled=True requires TELEGRAM_BOT_TOKEN")
        return self

settings = Settings()
```

## References

- [01-stack.md](01-stack.md) — library choices
- [02-architecture.md](02-architecture.md) — layered design
- [04-pipeline.md](04-pipeline.md) — pipeline.run usage
- [05-config.md](05-config.md) — config system detail
