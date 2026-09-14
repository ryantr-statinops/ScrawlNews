from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from src.config import settings


def shadow_database_path(run_id: str) -> Path:
    root = Path("data/dagster-shadow")
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{run_id}.db"


@contextmanager
def isolated_settings(run_id: str) -> Iterator[Path]:
    """Point existing services at a per-run database and restore settings."""
    previous_url = settings.database_url
    path = shadow_database_path(run_id)
    settings.database_url = f"sqlite:///{path}"
    try:
        yield path
    finally:
        settings.database_url = previous_url
