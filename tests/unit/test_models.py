from datetime import datetime
from src.models.article import Article
from src.models.summary import Summary
from src.models.run import PipelineRun


class TestArticleModel:
    def test_create_article_with_required_fields(self):
        article = Article(id="abc123", url="https://example.com", title="Test Title")
        assert article.id == "abc123"
        assert article.url == "https://example.com"
        assert article.title == "Test Title"
        assert article.source is None
        assert article.content is None
        assert article.summarized == 0

    def test_create_article_with_all_fields(self):
        fetched = datetime(2024, 1, 15, 10, 0, 0)
        article = Article(
            id="abc123",
            url="https://example.com",
            title="Test Title",
            source="TechCrunch",
            content="Some content",
            fetched_at=fetched,
            summarized=1,
        )
        assert article.source == "TechCrunch"
        assert article.content == "Some content"
        assert article.fetched_at == fetched
        assert article.summarized == 1


class TestSummaryModel:
    def test_create_summary_with_required_fields(self):
        summary = Summary(
            id="sum-1",
            article_id="abc123",
            summary_text="This is a summary",
            model_used="gpt-4o-mini",
        )
        assert summary.id == "sum-1"
        assert summary.article_id == "abc123"
        assert summary.summary_text == "This is a summary"
        assert summary.model_used == "gpt-4o-mini"
        assert summary.created_at is None

    def test_create_summary_with_timestamp(self):
        created = datetime(2024, 1, 15, 10, 30, 0)
        summary = Summary(
            id="sum-1",
            article_id="abc123",
            summary_text="Summary text",
            model_used="gpt-4o-mini",
            created_at=created,
        )
        assert summary.created_at == created


class TestPipelineRunModel:
    def test_create_pending_run(self):
        run = PipelineRun(id="run-1", status="pending")
        assert run.id == "run-1"
        assert run.status == "pending"
        assert run.task_id is None
        assert run.articles_fetched == 0
        assert run.summaries_generated == 0
        assert run.telegram_sent == 0
        assert run.error is None

    def test_create_completed_run(self):
        started = datetime(2024, 1, 15, 10, 0, 0)
        finished = datetime(2024, 1, 15, 10, 5, 0)
        run = PipelineRun(
            id="run-1",
            status="success",
            task_id="task-123",
            articles_fetched=20,
            summaries_generated=18,
            telegram_sent=1,
            started_at=started,
            finished_at=finished,
        )
        assert run.status == "success"
        assert run.task_id == "task-123"
        assert run.articles_fetched == 20
        assert run.summaries_generated == 18
        assert run.telegram_sent == 1
        assert run.started_at == started
        assert run.finished_at == finished

    def test_create_failed_run_with_error(self):
        run = PipelineRun(id="run-1", status="failed", error="LLM API timeout")
        assert run.status == "failed"
        assert run.error == "LLM API timeout"
