from src.models.article import Article


def test_save_and_get(article_repo):
    article = Article(id="abc123", url="https://example.com", title="Test")
    article_repo.save(article)
    retrieved = article_repo.get_by_id("abc123")
    assert retrieved is not None
    assert retrieved["url"] == "https://example.com"
    assert retrieved["title"] == "Test"


def test_dedup_by_url(article_repo):
    article = Article(id="abc123", url="https://example.com", title="Test")
    article_repo.save(article)
    article2 = Article(id="xyz789", url="https://example.com", title="Test 2")
    article_repo.save(article2)
    count = article_repo.count()
    assert count == 1


def test_exists(article_repo):
    article = Article(id="abc123", url="https://example.com", title="Test")
    article_repo.save(article)
    assert article_repo.exists("https://example.com") is True
    assert article_repo.exists("https://other.com") is False


def test_get_unsummarized(article_repo):
    article1 = Article(id="a1", url="https://a.com", title="A", summarized=0)
    article2 = Article(id="a2", url="https://b.com", title="B", summarized=1)
    article_repo.save(article1)
    article_repo.save(article2)
    unsummarized = article_repo.get_unsummarized(limit=10)
    assert len(unsummarized) == 1
    assert unsummarized[0]["id"] == "a1"


def test_mark_summarized(article_repo):
    article = Article(id="a1", url="https://a.com", title="A", summarized=0)
    article_repo.save(article)
    article_repo.mark_summarized("a1")
    article = article_repo.get_by_id("a1")
    assert article["summarized"] == 1


def test_count(article_repo):
    assert article_repo.count() == 0
    article = Article(id="a1", url="https://a.com", title="A")
    article_repo.save(article)
    assert article_repo.count() == 1


def test_get_recent(article_repo):
    article = Article(id="a1", url="https://a.com", title="A")
    article_repo.save(article)
    recent = article_repo.get_recent(days=7)
    assert len(recent) >= 1
    assert recent[0]["id"] == "a1"


def test_cleanup_old(article_repo):
    article = Article(id="a1", url="https://a.com", title="A")
    article_repo.save(article)
    article_repo.cleanup_old(days=0)
    assert article_repo.count() == 0
