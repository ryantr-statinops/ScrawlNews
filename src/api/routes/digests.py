from fastapi import APIRouter, HTTPException, Query

from src.config import settings
from src.repositories.digest_repo import DigestRepository

router = APIRouter()


def _repo() -> DigestRepository:
    return DigestRepository(settings.database_url)


@router.get("/api/digests")
def list_digests(category: str | None = None, limit: int = Query(20, ge=1, le=100)):
    return {"digests": _repo().list_recent(category=category, limit=limit)}


@router.get("/api/digests/{digest_id}")
def get_digest(digest_id: str):
    digest = _repo().get(digest_id)
    if digest is None:
        raise HTTPException(status_code=404, detail="Digest not found")
    return digest


@router.get("/api/digests/{digest_id}/articles")
def get_digest_articles(digest_id: str):
    if _repo().get(digest_id) is None:
        raise HTTPException(status_code=404, detail="Digest not found")
    return {"articles": _repo().articles(digest_id)}
