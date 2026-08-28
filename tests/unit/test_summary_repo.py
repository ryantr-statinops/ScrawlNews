import pytest
from src.models.summary import Summary
from src.repositories.summary_repo import SummaryRepository


def test_save_and_get(summary_repo):
    summary = Summary(id="s1", article_id="a1", summary_text="T", model_used="m")
    summary_repo.save(summary)
    retrieved = summary_repo.get_by_id("s1")
    assert retrieved is not None
    assert retrieved["summary_text"] == "T"
    assert retrieved["article_id"] == "a1"


def test_get_by_article(summary_repo):
    summary1 = Summary(id="s1", article_id="a1", summary_text="T1", model_used="m")
    summary2 = Summary(id="s2", article_id="a1", summary_text="T2", model_used="m")
    summary_repo.save(summary1)
    summary_repo.save(summary2)
    results = summary_repo.get_by_article("a1")
    assert len(results) == 2
    assert {r["id"] for r in results} == {"s1", "s2"}


def test_get_recent(summary_repo):
    summary = Summary(id="s1", article_id="a1", summary_text="T", model_used="m")
    summary_repo.save(summary)
    recent = summary_repo.get_recent(days=7)
    assert len(recent) >= 1
    assert recent[0]["id"] == "s1"


def test_count(summary_repo):
    assert summary_repo.count() == 0
    summary = Summary(id="s1", article_id="a1", summary_text="T", model_used="m")
    summary_repo.save(summary)
    assert summary_repo.count() == 1


def test_get_by_id_not_found(summary_repo):
    result = summary_repo.get_by_id("nonexistent")
    assert result is None
