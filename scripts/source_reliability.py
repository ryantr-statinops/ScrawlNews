"""Read-only RSS and article extraction reliability probe."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import quote

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.services.scrawler import ScrawlerService  # noqa: E402

DEFAULT_CATEGORIES = "technology,business,world,science"
DEFAULT_OUTPUT = "source_reliability.json"


def reliability_band(rate: float) -> str:
    if rate >= 95:
        return "healthy"
    if rate >= 75:
        return "warning"
    return "fallback_target"


async def collect_report(
    *,
    runs: int = 3,
    limit: int = 20,
    categories: list[str] | None = None,
    country: str = "VN",
    clock: Any = datetime.now,
    timer: Any = perf_counter,
) -> dict[str, Any]:
    requested_categories = categories or DEFAULT_CATEGORIES.split(",")
    attempts: list[dict[str, Any]] = []

    for attempt_number in range(1, runs + 1):
        service = ScrawlerService()
        category_results: list[dict[str, Any]] = []
        for category in requested_categories:
            started = timer()
            try:
                region = country.upper()
                language = "vi" if region == "VN" else "en"
                feed_url = (
                    f"https://news.google.com/rss/search?q={quote(category)}"
                    f"&hl={language}&gl={region}&ceid={region}:{language}"
                )
                articles = await service._fetch_with_event(
                    {
                        "id": f"google-{category}",
                        "name": f"Google News · {category}",
                        "category": category,
                        "country": country,
                        "url": feed_url,
                    },
                    limit,
                )
                event = service.fetch_events[-1]
                category_results.append(
                    {
                        "category": category,
                        "status": "success",
                        "fetched_count": len(articles),
                        "content_count": sum(
                            bool(article.content and article.content.strip())
                            for article in articles
                        ),
                        "latency_ms": event["latency_ms"],
                        "error": None,
                    }
                )
            except Exception as exc:
                elapsed = round((timer() - started) * 1000)
                category_results.append(
                    {
                        "category": category,
                        "status": "failure",
                        "fetched_count": 0,
                        "content_count": 0,
                        "latency_ms": elapsed,
                        "error": type(exc).__name__,
                    }
                )
        attempts.append({"attempt": attempt_number, "categories": category_results})

    requests = [result for attempt in attempts for result in attempt["categories"]]

    def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
        request_count = len(results)
        successes = sum(result["status"] == "success" for result in results)
        fetched = sum(result["fetched_count"] for result in results)
        content = sum(result["content_count"] for result in results)
        rss_rate = 100 * successes / request_count if request_count else None
        extraction_rate = 100 * content / fetched if fetched else None
        return {
            "category_request_count": request_count,
            "rss_success_count": successes,
            "fetched_count": fetched,
            "content_count": content,
            "rss_success_rate": round(rss_rate, 2) if rss_rate is not None else None,
            "rss_band": reliability_band(rss_rate) if rss_rate is not None else "unverifiable",
            "content_extraction_rate": round(extraction_rate, 2)
            if extraction_rate is not None
            else None,
            "content_band": reliability_band(extraction_rate)
            if extraction_rate is not None
            else "unverifiable",
            "average_latency_ms": round(
                sum(result["latency_ms"] for result in results) / request_count, 2
            )
            if request_count
            else None,
        }

    category_aggregates = {
        category: aggregate([result for result in requests if result["category"] == category])
        for category in requested_categories
    }
    fallback_targets = []
    for category, metrics in category_aggregates.items():
        if metrics["rss_band"] == "fallback_target":
            fallback_targets.append(
                {
                    "category": category,
                    "metric": "rss_success_rate",
                    "recommendation": "alternate/custom RSS",
                }
            )
        if metrics["content_band"] == "fallback_target":
            fallback_targets.append(
                {
                    "category": category,
                    "metric": "content_extraction_rate",
                    "recommendation": "Readability-lxml before Playwright",
                }
            )

    generated = clock(UTC).isoformat().replace("+00:00", "Z")
    return {
        "generated_at": generated,
        "parameters": {
            "runs": runs,
            "limit": limit,
            "categories": requested_categories,
            "country": country,
        },
        "attempts": attempts,
        "aggregates": {**aggregate(requests), "categories": category_aggregates},
        "fallback_targets": fallback_targets,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--categories", default=DEFAULT_CATEGORIES)
    parser.add_argument("--country", default="VN")
    parser.add_argument("--output", type=Path, default=Path(DEFAULT_OUTPUT))
    args = parser.parse_args()
    if args.runs < 1 or args.limit < 1:
        parser.error("--runs and --limit must be positive")
    return args


async def _run(args: argparse.Namespace) -> None:
    report = await collect_report(
        runs=args.runs,
        limit=args.limit,
        categories=[
            category.strip() for category in args.categories.split(",") if category.strip()
        ],
        country=args.country,
    )
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    asyncio.run(_run(parse_args()))


if __name__ == "__main__":
    main()
