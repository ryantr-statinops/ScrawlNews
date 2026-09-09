from typing import Literal

from fastapi import APIRouter, Query

from src.config import settings
from src.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
Window = Literal["1h", "4h", "12h", "24h", "7d", "30d"]


def _service() -> AnalyticsService:
    return AnalyticsService(settings.database_url)


@router.get("/overview")
def overview(
    window: Window = "24h",
    category: str | None = None,
    source_id: str | None = None,
    provider: str | None = None,
    model: str | None = None,
):
    return _service().overview(window, category, source_id, provider, model)


@router.get("/content")
def content(
    window: Window = "24h",
    category: str | None = None,
    source_id: str | None = None,
):
    return _service().content(window, category, source_id)


@router.get("/pipeline")
def pipeline(window: Window = "24h"):
    return _service().pipeline(window)


@router.get("/sources")
def sources(
    window: Window = "24h", category: str | None = None, country: str | None = None
):
    return _service().sources(window, category, country)


@router.get("/ai-usage")
def ai_usage(
    window: Window = "24h",
    provider: str | None = None,
    model: str | None = None,
):
    return _service().ai_usage(window, provider, model)


@router.get("/drilldown")
def drilldown(
    kind: Literal["articles", "runs", "stages", "sources", "llm"],
    window: Window = "24h",
    category: str | None = None,
    source_id: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    run_id: str | None = None,
    operation: str | None = None,
    limit: int = Query(50, ge=1, le=100),
):
    return _service().drilldown(
        kind,
        window,
        category,
        source_id,
        provider,
        model,
        run_id,
        operation,
        limit,
    )
