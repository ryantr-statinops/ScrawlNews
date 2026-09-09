from src.models.article import Article
from src.models.digest import Digest
from src.repositories.article_repo import ArticleRepository
from src.repositories.digest_repo import DigestRepository


def test_digest_repo_saves_and_loads_article_links(temp_db):
    repo = DigestRepository(f"sqlite:///{temp_db}")
    ArticleRepository(f"sqlite:///{temp_db}").save(Article("a1", "https://a1", "A1"))
    repo.save(Digest("d1", "technology", "Tech", "Summary", 1, "test"), ["a1"])
    assert repo.get("d1")["article_count"] == 1
    assert repo.articles("d1")[0]["id"] == "a1"
