from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes import analytics


@pytest.mark.parametrize(
    "handler,args,expected_key",
    [
        (analytics.overview, ("24h", None, None, None, None), "kpis"),
        (analytics.content, ("24h", None, None), "velocity"),
        (analytics.pipeline, ("24h",), "stages"),
        (analytics.sources, ("24h", None, None), "sources"),
        (analytics.ai_usage, ("24h", None, None), "providers"),
        (
            analytics.drilldown,
            ("articles", "24h", None, None, None, None, None, None, 50),
            "records",
        ),
    ],
)
def test_analytics_handlers_return_empty_safe_responses(handler, args, expected_key):
    data = handler(*args)

    assert data["period"]["window"] == "24h"
    assert data["period"]["previous"]["to"] == data["period"]["current"]["from"]
    assert expected_key in data


def test_openapi_exposes_analytics_and_legacy_stats_routes():
    paths = app.openapi()["paths"]

    assert "/api/stats" in paths
    assert {
        "/api/analytics/overview",
        "/api/analytics/content",
        "/api/analytics/pipeline",
        "/api/analytics/sources",
        "/api/analytics/ai-usage",
        "/api/analytics/drilldown",
    } <= paths.keys()
    window_schema = paths["/api/analytics/overview"]["get"]["parameters"][0]["schema"]
    assert window_schema["enum"] == ["1h", "4h", "12h", "24h", "7d", "30d"]

def test_ai_usage_api_exposes_real_priced_cost_and_missing_alert(monkeypatch, tmp_path):
    from src.api.routes import analytics
    from src.repositories.config_repo import ConfigRepository
    from src.repositories.telemetry_repo import TelemetryRepository
    from src.services.analytics import AnalyticsService

    db = f"sqlite:///{tmp_path}/api-cost.db"
    clock = datetime(2024, 2, 15, 12, tzinfo=UTC)
    monkeypatch.setattr(analytics, "_service", lambda: AnalyticsService(db, now=clock))
    repo = TelemetryRepository(db)
    config = ConfigRepository(db)
    config.set("llm_price_snapshot_json", '{"p/m":{"input_per_million_usd":2,"output_per_million_usd":4}}')
    config.set("llm_monthly_budget_usd", "29")
    repo.record_llm_usage(operation="summary", provider="p", model="m", input_tokens=7_250_000, output_tokens=0, total_tokens=7_250_000, latency_ms=1, status="success", occurred_at="2024-02-15T11:00:00")
    client = TestClient(app)
    response = client.get("/api/analytics/ai-usage?window=24h")
    assert response.status_code == 200
    assert response.json()["cost"]["month_to_date_usd"] == 14.5
    assert response.json()["cost"]["monthly_estimate_usd"] == 29
    assert response.json()["cost"]["alert"] is True
    repo.record_llm_usage(operation="summary", provider="unknown", model="m", input_tokens=13, output_tokens=2, total_tokens=15, latency_ms=1, status="success", occurred_at="2024-02-15T11:30:00")
    incomplete = client.get("/api/analytics/ai-usage?window=24h").json()["cost"]
    assert incomplete["alert"] is False
    assert incomplete["unpriced_models"] == ["unknown/m"]
    assert incomplete["unpriced_tokens"] == 15
