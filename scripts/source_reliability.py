"""Read-only RSS and article extraction reliability probe."""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from src.services.scrawler import ScrawlerService

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
                articles = await service._fetch_with_event(
                    {
                        "id": f"google-{category}",
                        "name": f"Google News · {category}",
                        "category": category,
                        "country": country,
                    },
                    limit,
                )
                event = service.fetch_events[-1]
                category_results.append(
                    {
                        "category": category,
                        "status": "success",
                        "fetched_count": len(articles),
                        "content_count": sum(bool(article.content and article.content.strip()) for article in articles),
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
    request_count = len(requests)
    fetched_count = sum(result["fetched_count"] for result in requests)
    content_count = sum(result["content_count"] for result in requests)
    rss_rate = (100 * sum(result["status"] == "success" for result in requests) / request_count) if request_count else 0.0
    content_rate = (100 * content_count / fetched_count) if fetched_count else 0.0
    fallback_targets: list[str] = []
    if reliability_band(rss_rate) == "fallback_target":
        fallback_targets.append("alternate/custom RSS")
    if reliability_band(content_rate) == "fallback_target":
        fallback_targets.append("Readability-lxml before Playwright")

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
        "aggregates": {
            "category_request_count": request_count,
            "rss_success_count": sum(result["status"] == "success" for result in requests),
            "fetched_count": fetched_count,
            "content_count": content_count,
            "rss_success_rate": round(rss_rate, 2),
            "rss_band": reliability_band(rss_rate),
            "content_extraction_rate": round(content_rate, 2),
            "content_band": reliability_band(content_rate),
            "average_latency_ms": round(sum(result["latency_ms"] for result in requests) / request_count, 2) if request_count else 0.0,
        },
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
        categories=[category.strip() for category in args.categories.split(",") if category.strip()],
        country=args.country,
    )
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    asyncio.run(_run(parse_args()))


if __name__ == "__main__":
    main()
