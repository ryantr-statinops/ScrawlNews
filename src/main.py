import argparse
import asyncio

from src.config import settings
from src.worker.tasks import pipeline_run


def main():
    parser = argparse.ArgumentParser(description="ScrawlNews pipeline CLI")
    parser.add_argument("--dry-run", action="store_true", help="run without Telegram")
    parser.add_argument("--limit", type=int, default=None, help="fetch limit override")
    args = parser.parse_args()

    # Run pipeline directly without Celery for CLI
    result = pipeline_run(args.limit, dry_run=args.dry_run)
    print(result)


if __name__ == "__main__":
    main()
