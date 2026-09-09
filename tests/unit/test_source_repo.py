from src.models.source import NewsSource
from src.repositories.source_repo import NewsSourceRepository


def test_source_repo_crud_and_search(temp_db):
    repo = NewsSourceRepository(f"sqlite:///{temp_db}")
    repo.save(NewsSource("tech", "Tech feed", "https://example.com/tech", "technology"))
    repo.save(NewsSource("news", "World feed", "https://example.com/world", "world", enabled=0))

    assert repo.get("tech")["name"] == "Tech feed"
    assert len(repo.list(query="technology")) == 1
    assert len(repo.list(enabled=True)) == 1
    repo.update_status("tech", "ok")
    assert repo.get("tech")["last_status"] == "ok"
    assert repo.delete("news") is True
    assert repo.get("news") is None
