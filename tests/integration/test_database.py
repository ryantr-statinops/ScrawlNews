import pytest
from src.repositories.article_repo import ArticleRepository
from src.repositories.summary_repo import SummaryRepository
from src.repositories.run_repo import PipelineRunRepository
from src.models.article import Article
from src.models.summary import Summary
from src.models.run import PipelineRun


def test_database_migration(temp_db):
    article_repo = ArticleRepository(f"sqlite:///{temp_db}")
    import sqlite3
    conn = sqlite3.connect(temp_db)
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'").fetchone()
    assert row is not None
    conn.close()


def test_article_dedup_integration(temp_db):
    article_repo = ArticleRepository(f"sqlite:///{temp_db}")
    article = Article(id="a1", url="https://a.com", title="A")
    article_repo.save(article)
    article_repo.save(article)
    assert article_repo.count() == 1


def test_cleanup_integration(temp_db):
    article_repo = ArticleRepository(f"sqlite:///{temp_db}")
    article = Article(id="a1", url="https://a.com", title="A")
    article_repo.save(article)
    article_repo.cleanup_old(days=0)
    assert article_repo.count() == 0


def test_full_crud_cycle(temp_db):
    article_repo = ArticleRepository(f"sqlite:///{temp_db}")
    summary_repo = SummaryRepository(f"sqlite:///{temp_db}")
    run_repo = PipelineRunRepository(f"sqlite:///{temp_db}")

    article = Article(id="a1", url="https://a.com", title="A")
    article_repo.save(article)
    assert article_repo.count() == 1

    summary = Summary(id="s1", article_id="a1", summary_text="T", model_used="m")
    summary_repo.save(summary)
    assert summary_repo.count() == 1

    run = PipelineRun(id="r1", status="success")
    run_repo.create(run)
    assert run_repo.count() == 1

    article_repo.mark_summarized("a1")
    assert article_repo.get_by_id("a1")["summarized"] == 1
