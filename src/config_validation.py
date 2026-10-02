import json
import re
from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class ModelPrice:
    input_per_million_usd: Decimal
    output_per_million_usd: Decimal

def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result

def parse_price_snapshot(value: str) -> dict[str, ModelPrice]:
    if not isinstance(value, str):
        raise ValueError("Price snapshot must be JSON")
    try:
        raw = json.loads(value, parse_float=Decimal, parse_int=Decimal,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite price")),
                         object_pairs_hook=_unique_object)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid price snapshot JSON") from exc
    if not isinstance(raw, dict):
        raise ValueError("Price snapshot must be an object")
    prices: dict[str, ModelPrice] = {}
    required = {"input_per_million_usd", "output_per_million_usd"}
    for key, rates in raw.items():
        if not isinstance(key, str) or "/" not in key or key.startswith("/") or key.endswith("/"):
            raise ValueError("Price key must be provider/model")
        if not isinstance(rates, dict) or rates.keys() != required:
            raise ValueError("Price rates must have exactly input and output fields")
        values = []
        for field in ("input_per_million_usd", "output_per_million_usd"):
            rate = rates[field]
            if not isinstance(rate, Decimal) or not rate.is_finite() or rate < 0:
                raise ValueError("Price rates must be finite nonnegative numbers")
            values.append(rate)
        prices[key] = ModelPrice(*values)
    return prices

def canonical_price_snapshot(value: str) -> str:
    prices = parse_price_snapshot(value)
    fields = ("input_per_million_usd", "output_per_million_usd")
    return "{" + ",".join(
        json.dumps(key) + ":{" + ",".join(
            json.dumps(field) + ":" + str(getattr(price, field)) for field in fields
        ) + "}" for key, price in sorted(prices.items())
    ) + "}"

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
