from src.models.article import Article
from src.models.run import PipelineRun
from src.models.summary import Summary
from src.repositories.article_repo import ArticleRepository
from src.repositories.run_repo import PipelineRunRepository
from src.repositories.summary_repo import SummaryRepository


def test_full_pipeline_dry_run(temp_db):
    article_repo = ArticleRepository(f"sqlite:///{temp_db}")
    summary_repo = SummaryRepository(f"sqlite:///{temp_db}")
    run_repo = PipelineRunRepository(f"sqlite:///{temp_db}")

    run = PipelineRun(id="run-1", status="success", articles_fetched=2, summaries_generated=2)
    run_repo.create(run)

    article = Article(id="a1", url="https://a.com", title="A", summarized=1)
    article_repo.save(article)

    summary = Summary(id="s1", article_id="a1", summary_text="T", model_used="m")
    summary_repo.save(summary)

    assert article_repo.count() == 1
    assert summary_repo.count() == 1
    assert run_repo.count() == 1


def test_pipeline_skip_summarized(temp_db):
    article_repo = ArticleRepository(f"sqlite:///{temp_db}")
    article1 = Article(id="a1", url="https://a.com", title="A", summarized=1)
    article2 = Article(id="a2", url="https://b.com", title="B", summarized=0)
    article_repo.save(article1)
    article_repo.save(article2)
    unsummarized = article_repo.get_unsummarized(limit=10)
    assert len(unsummarized) == 1
    assert unsummarized[0]["id"] == "a2"
