"""Create and restore consistent SQLite backups for the local deployment."""

from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


def database_path() -> Path:
    url = os.getenv("DATABASE_URL", "sqlite:///data/scrawlnews.db")
    if not url.startswith("sqlite:///"):
        raise SystemExit("DATABASE_URL must use sqlite:///... for local backups")
    return Path(url.removeprefix("sqlite:///"))


def check_integrity(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        raise SystemExit(f"SQLite integrity check failed for {path}")


def copy_database(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as source_connection, sqlite3.connect(target) as target_connection:
        source_connection.backup(target_connection)
    check_integrity(target)


def backup(path: Path | None) -> Path:
    source = path or database_path()
    if not source.exists():
        raise SystemExit(f"SQLite database does not exist: {source}")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    target = Path("backups") / f"{source.stem}-{timestamp}.db"
    copy_database(source, target)
    print(f"Created backup: {target}")
    return target


def restore(source: Path, target: Path | None) -> None:
    destination = target or database_path()
    if not source.exists():
        raise SystemExit(f"Backup does not exist: {source}")
    check_integrity(source)
    if destination.exists():
        safety = destination.with_suffix(
            f".pre-restore-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.db"
        )
        copy_database(destination, safety)
        print(f"Created safety backup: {safety}")
    copy_database(source, destination)
    print(f"Restored database: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("--source", type=Path)

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("source", type=Path)
    restore_parser.add_argument("--target", type=Path)
    args = parser.parse_args()

    if args.command == "backup":
        backup(args.source)
    else:
        restore(args.source, args.target)


if __name__ == "__main__":
    main()
