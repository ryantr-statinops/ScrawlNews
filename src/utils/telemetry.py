import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from time import perf_counter

from src.repositories.telemetry_repo import TelemetryRepository

logger = logging.getLogger(__name__)


@contextmanager
def track_stage(
    repository: TelemetryRepository, run_id: str, stage: str
) -> Iterator[dict[str, int | None]]:
    started_at = datetime.now(UTC).replace(tzinfo=None)
    started = perf_counter()
    metadata: dict[str, int | None] = {"item_count": None}
    try:
        yield metadata
    except BaseException as exc:
        _record(
            repository,
            run_id,
            stage,
            "failed",
            started_at,
            started,
            metadata["item_count"],
            type(exc).__name__,
        )
        raise
    else:
        _record(
            repository,
            run_id,
            stage,
            "success",
            started_at,
            started,
            metadata["item_count"],
            None,
        )


def _record(
    repository: TelemetryRepository,
    run_id: str,
    stage: str,
    status: str,
    started_at: datetime,
    started: float,
    item_count: int | None,
    error_class: str | None,
) -> None:
    try:
        repository.record_stage(
            run_id=run_id,
            stage=stage,
            status=status,
            duration_ms=round((perf_counter() - started) * 1000),
            item_count=item_count,
            error_class=error_class,
            started_at=started_at.isoformat(),
            finished_at=datetime.now(UTC).replace(tzinfo=None).isoformat(),
        )
    except (sqlite3.Error, OSError):
        logger.warning("Unable to record pipeline telemetry", exc_info=True)
