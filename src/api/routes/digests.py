import asyncio

from fastapi import APIRouter, HTTPException, Query

from src.config import settings
from src.models.article import Article
from src.models.summary import Summary
from src.repositories.article_repo import ArticleRepository
from src.repositories.digest_repo import DigestRepository
from src.repositories.summary_repo import SummaryRepository
from src.services.digest_service import DigestService

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


@router.post("/api/digests/regenerate")
def regenerate_digest(payload: dict):
    category = str(payload.get("category", "")).strip().lower()
    if not category:
        raise HTTPException(status_code=422, detail="category is required")
    article_repo = ArticleRepository(settings.database_url)
    summary_repo = SummaryRepository(settings.database_url)
    articles = [Article(**row) for row in article_repo.get_recent(limit=100) if row.get("category") == category]
    summaries_by_article = {
        row["article_id"]: Summary(**row)
        for article in articles
        for row in summary_repo.get_by_article(article.id)
    }
    summaries = [summaries_by_article[article.id] for article in articles if article.id in summaries_by_article]
    digest = asyncio.run(DigestService().execute(category, articles, summaries))
    return _repo().save(digest, [article.id for article in articles])
