import re
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def validate_schedule_times(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("schedule_times must be nonempty")
    entries = [item.strip() for item in value.split(",")]
    if not entries or any(not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", item) for item in entries):
        raise ValueError("schedule_times must contain HH:MM values")
    if len(set(entries)) != len(entries):
        raise ValueError("schedule_times must be unique")
    return ",".join(entries)


def validate_timezone(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("timezone must be nonempty")
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("timezone must be an IANA timezone") from exc
    return value


def _validate_url(value: str, schemes: set[str]) -> str:
    if not isinstance(value, str):
        raise ValueError("URL must be a string")
    parts = urlsplit(value)
    try:
        valid = parts.scheme in schemes and bool(parts.hostname) and parts.port != 0
    except ValueError:
        valid = False
    if not valid or any(c.isspace() for c in value):
        raise ValueError("Invalid URL")
    return value


def validate_http_url(value: str) -> str:
    return _validate_url(value, {"http", "https"})


def validate_redis_url(value: str) -> str:
    return _validate_url(value, {"redis", "rediss"})


def validate_sqlite_url(value: str) -> str:
    if not isinstance(value, str) or not value.startswith("sqlite:///") or not value[10:]:
        raise ValueError("sqlite URL must use sqlite:/// with a path")
    return value
