from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
import trafilatura

from scripts import source_reliability
from src.models.article import Article
from src.services.scrawler import ScrawlerService
from src.utils.errors import ScrawlerError


@pytest.mark.parametrize(
    ("rate", "expected"),
    [(74.9, "fallback_target"), (75, "warning"), (94.9, "warning"), (95, "healthy")],
)
def test_reliability_band_boundaries(rate, expected):
    assert source_reliability.reliability_band(rate) == expected


@pytest.mark.asyncio
async def test_report_is_deterministic_and_uses_rss_extraction_and_mocked_clock():
    fixed_time = datetime(2026, 1, 2, tzinfo=UTC)

    async def mocked_rss(*args, **kwargs):
        downloaded = trafilatura.fetch_url("https://example.test/story")
        content = trafilatura.extract(downloaded)
        return [Article(id="1", url="https://example.test/story", title="Story", content=content)]

    with (
        patch.object(ScrawlerService, "fetch_rss", new_callable=AsyncMock, side_effect=mocked_rss),
        patch("trafilatura.fetch_url", return_value="<article>mock page</article>"),
        patch("trafilatura.extract", return_value="Extracted article text"),
        patch("src.services.scrawler.perf_counter", return_value=1.0),
    ):
        first = await source_reliability.collect_report(
            runs=1,
            limit=5,
            categories=["technology"],
            clock=lambda tz: fixed_time,
            timer=lambda: 1.0,
        )
        second = await source_reliability.collect_report(
            runs=1,
            limit=5,
            categories=["technology"],
            clock=lambda tz: fixed_time,
            timer=lambda: 1.0,
        )

    assert first == second
    assert first["generated_at"] == "2026-01-02T00:00:00Z"
    assert first["attempts"][0]["categories"][0]["fetched_count"] == 1
    assert first["aggregates"]["content_extraction_rate"] == 100
    assert first["aggregates"]["rss_band"] == "healthy"


@pytest.mark.asyncio
async def test_report_sanitizes_rss_error_to_class_name():
    with (
        patch.object(
            ScrawlerService,
            "fetch_rss",
            new_callable=AsyncMock,
            side_effect=ScrawlerError("private URL and token=secret"),
        ),
        patch("src.services.scrawler.perf_counter", return_value=1.0),
    ):
        report = await source_reliability.collect_report(
            runs=1,
            categories=["world"],
            clock=lambda tz: datetime(2026, 1, 2, tzinfo=UTC),
            timer=lambda: 1.0,
        )

    outcome = report["attempts"][0]["categories"][0]
    assert outcome["status"] == "failure"
    assert outcome["error"] == "ScrawlerError"
    assert "secret" not in str(report)
    assert report["aggregates"]["content_band"] == "unverifiable"
    assert report["fallback_targets"] == [
        {
            "category": "world",
            "metric": "rss_success_rate",
            "recommendation": "alternate/custom RSS",
        }
    ]


@pytest.mark.asyncio
async def test_country_url_and_category_specific_extraction_target():
    urls = []

    async def mocked_rss(*args, **kwargs):
        urls.append(kwargs["source_url"])
        return [Article(id="1", url="https://example.test/story", title="Story", content=None)]

    with (
        patch.object(ScrawlerService, "fetch_rss", new_callable=AsyncMock, side_effect=mocked_rss),
        patch("src.services.scrawler.perf_counter", return_value=1.0),
    ):
        report = await source_reliability.collect_report(
            runs=1,
            categories=["business"],
            country="US",
            clock=lambda tz: datetime(2026, 1, 2, tzinfo=UTC),
            timer=lambda: 1.0,
        )

    assert "gl=US&ceid=US:en" in urls[0]
    assert report["aggregates"]["categories"]["business"]["content_band"] == "fallback_target"
    assert report["fallback_targets"] == [
        {
            "category": "business",
            "metric": "content_extraction_rate",
            "recommendation": "Readability-lxml before Playwright",
        }
    ]
