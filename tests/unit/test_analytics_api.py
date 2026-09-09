import pytest

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
