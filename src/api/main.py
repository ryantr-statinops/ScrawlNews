import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routes import articles, config, health, logs, runs, stats, summaries
from src.config import settings
from src.utils.errors import (
    ConfigError,
    MessengerError,
    NotFoundError,
    ScrawlerError,
    ScrawlError,
    SynthesizerError,
)
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging(settings.log_level)
    logger.info("Dashboard started")
    yield
    logger.info("Dashboard shutting down")


app = FastAPI(title="ScrawlNews Dashboard", version="0.2.0", lifespan=lifespan)


@app.exception_handler(ScrawlError)
async def domain_error_handler(request: Request, exc: ScrawlError):
    if isinstance(exc, NotFoundError):
        status = 404
    elif isinstance(exc, ConfigError):
        status = 400
    elif isinstance(exc, (ScrawlerError, SynthesizerError, MessengerError)):
        status = 503 if exc.retryable else 502
    else:
        status = 500
    if status >= 500:
        logger.error("Domain operation failed", exc_info=exc)
    return JSONResponse(status_code=status, content={"error": exc.public_message})


app.include_router(articles.router)
app.include_router(runs.router)
app.include_router(config.router)
app.include_router(health.router)
app.include_router(summaries.router)
app.include_router(logs.router)
app.include_router(stats.router)
