import argparse
import logging

from src.utils.logging import setup_logging
from src.worker.tasks import pipeline_run


def main():
    parser = argparse.ArgumentParser(description="ScrawlNews pipeline CLI")
    parser.add_argument("--dry-run", action="store_true", help="run without Telegram")
    parser.add_argument("--limit", type=int, default=None, help="fetch limit override")
    args = parser.parse_args()

    setup_logging("INFO")
    result = pipeline_run(args.limit, dry_run=args.dry_run)
    logging.getLogger("cli").info("Pipeline finished", extra={"result": result})


if __name__ == "__main__":
    main()
