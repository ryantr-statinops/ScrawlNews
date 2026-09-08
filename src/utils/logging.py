import json
import logging
import sys
import traceback
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """Stdlib formatter that emits one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        log: dict = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log["exc"] = "".join(traceback.format_exception(*record.exc_info))
        if hasattr(record, "run_id"):
            log["run_id"] = record.run_id
        if hasattr(record, "stage"):
            log["stage"] = record.stage
        return json.dumps(log, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger for JSON output to stdout.

    Call once at process startup (FastAPI lifespan or Celery worker_init).
    Existing ``logging.getLogger(__name__)`` calls across the codebase
    automatically produce structured JSON — no migration needed.
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)
