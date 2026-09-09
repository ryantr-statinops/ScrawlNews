import hashlib
import xml.etree.ElementTree as ET

import httpx
from fastapi import APIRouter, HTTPException, Query

from src.config import settings
from src.models.source import NewsSource
from src.repositories.source_repo import NewsSourceRepository
from src.services.source_catalog import DEFAULT_SOURCES

router = APIRouter()


def _repo() -> NewsSourceRepository:
    return NewsSourceRepository(settings.database_url)


def _is_custom_url(url: str) -> bool:
    return url.startswith(("http://", "https://"))


def _source_rows(query: str | None = None, enabled: bool | None = None) -> list[dict]:
    stored = _repo().list(query=query, enabled=enabled)
    stored_ids = {row["id"] for row in stored}
    defaults = [source.__dict__.copy() for source in DEFAULT_SOURCES if source.id not in stored_ids]
    rows = defaults + stored
    if query:
        term = query.lower()
        rows = [
            row
            for row in rows
            if term in row["name"].lower()
            or term in row["url"].lower()
            or term in (row.get("category") or "").lower()
        ]
    if enabled is not None:
        rows = [row for row in rows if bool(row.get("enabled")) is enabled]
    return rows


@router.get("/api/sources")
def list_sources(query: str | None = Query(None, alias="q"), enabled: bool | None = None):
    return {"sources": _source_rows(query=query, enabled=enabled)}


@router.post("/api/sources")
def create_source(payload: dict):
    name = str(payload.get("name", "")).strip()
    url = str(payload.get("url", "")).strip()
    if not name or not _is_custom_url(url):
        raise HTTPException(status_code=422, detail="name and HTTP(S) url are required")
    source_id = hashlib.sha256(url.encode()).hexdigest()[:16]
    source = NewsSource(
        id=source_id,
        name=name,
        url=url,
        category=str(payload.get("category") or "").strip() or None,
        country=str(payload.get("country") or "VN").strip().upper(),
        city=str(payload.get("city") or "").strip() or None,
        enabled=1 if payload.get("enabled", True) else 0,
    )
    return _repo().save(source)


@router.put("/api/sources/{source_id}")
def update_source(source_id: str, payload: dict):
    existing = _repo().get(source_id)
    if existing is None:
        existing = next((source.__dict__.copy() for source in DEFAULT_SOURCES if source.id == source_id), None)
    if existing is None:
        raise HTTPException(status_code=404, detail="Source not found")
    url = str(payload.get("url", existing["url"])).strip()
    if not _is_custom_url(url):
        raise HTTPException(status_code=422, detail="HTTP(S) url is required")
    source = NewsSource(
        id=source_id,
        name=str(payload.get("name", existing["name"])).strip(),
        url=url,
        category=payload.get("category", existing["category"]),
        country=str(payload.get("country", existing["country"])).upper(),
        city=payload.get("city", existing["city"]),
        enabled=1 if payload.get("enabled", existing["enabled"]) else 0,
    )
    return _repo().save(source)


@router.delete("/api/sources/{source_id}")
def delete_source(source_id: str):
    if not _repo().delete(source_id):
        raise HTTPException(status_code=404, detail="Source not found")
    return {"deleted": source_id}


@router.post("/api/sources/{source_id}/test")
def test_source(source_id: str):
    source = next((row for row in _source_rows() if row["id"] == source_id), None)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    if not _is_custom_url(source["url"]):
        return {"source_id": source_id, "status": "ok", "message": "Built-in source"}
    try:
        response = httpx.get(source["url"], timeout=10, follow_redirects=True)
        response.raise_for_status()
        ET.fromstring(response.text)
        _repo().update_status(source_id, "ok")
        return {"source_id": source_id, "status": "ok", "message": "Valid RSS/Atom feed"}
    except (httpx.HTTPError, ET.ParseError) as exc:
        _repo().update_status(source_id, "error", str(exc))
        return {"source_id": source_id, "status": "error", "message": "Invalid or unavailable feed"}
