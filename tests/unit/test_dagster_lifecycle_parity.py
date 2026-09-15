import hashlib
import json
from dataclasses import replace

from src.dagster_project.comparison import PipelineExecution, PipelineInput, run_comparison
from src.models.digest import Digest
from src.models.summary import Summary


def _fixture_pipeline(pipeline_input, sample_articles):
    articles = tuple(
        replace(article, category=pipeline_input.categories[0])
        for article in sample_articles[: pipeline_input.fetch_limit]
    )
    summaries = tuple(
        Summary(
            id=f"summary-{article.id}",
            article_id=article.id,
            summary_text=f"Summary for {article.id}",
            model_used="fallback",
        )
        for article in articles
    )
    digests = (
        Digest(
            id=f"digest-{pipeline_input.categories[0]}",
            category=pipeline_input.categories[0],
            title="Technology briefing",
            digest_text="Fixture digest",
            article_count=len(articles),
            model_used="fallback",
        ),
    )
    return PipelineExecution(
        articles=articles,
        summaries=summaries,
        digests=digests,
        duplicate_count=0,
        telegram_sent=0,
        domain_db_mutated=False,
        stage_status=(
            ("ingestion", "success"),
            ("extraction", "success"),
            ("normalization", "success"),
            ("summarization", "success"),
            ("digest", "success"),
            ("delivery", "skipped"),
        ),
    )


def test_fixture_celery_and_dagster_have_lifecycle_parity(sample_articles, tmp_path):
    production_db = tmp_path / "scrawlnews.db"
    production_db.write_bytes(b"production-fixture-db")
    before = hashlib.sha256(production_db.read_bytes()).hexdigest()
    pipeline_input = PipelineInput(fetch_limit=2, categories=("technology",))

    report = run_comparison(
        pipeline_input,
        lambda value: _fixture_pipeline(value, sample_articles),
        lambda value: _fixture_pipeline(value, sample_articles),
    )

    assert report.parity.passed is True
    assert report.celery.article_count == 2
    assert report.dagster.summary_count == 2
    assert report.celery.digest_count == report.dagster.digest_count == 1
    assert report.celery.telegram_sent == report.dagster.telegram_sent == 0
    assert report.celery.domain_db_mutated is False
    assert report.dagster.domain_db_mutated is False
    assert hashlib.sha256(production_db.read_bytes()).hexdigest() == before


def test_partial_failure_is_parity_safe(sample_articles):
    pipeline_input = PipelineInput(fetch_limit=1, categories=("technology",))
    failed_execution = PipelineExecution(
        articles=(sample_articles[0],),
        summaries=(
            Summary("summary-1", sample_articles[0].id, "Fixture summary", "fallback"),
        ),
        error_stage="digest",
        telegram_sent=0,
        domain_db_mutated=False,
        stage_status=(("summarization", "success"), ("digest", "failed")),
    )

    report = run_comparison(
        pipeline_input,
        lambda _: failed_execution,
        lambda _: failed_execution,
    )

    assert report.parity.passed is True
    assert report.celery.error_stage == report.dagster.error_stage == "digest"
    assert report.celery.stage_status[-1] == ("digest", "failed")
    assert report.celery.telegram_sent == 0


def test_retry_does_not_add_delivery_or_leak_secrets(sample_articles):
    pipeline_input = PipelineInput(fetch_limit=1, categories=("technology",))
    execution = _fixture_pipeline(pipeline_input, sample_articles)

    first_report = run_comparison(pipeline_input, lambda _: execution, lambda _: execution)
    retry_report = run_comparison(pipeline_input, lambda _: execution, lambda _: execution)

    assert first_report.celery.telegram_sent == retry_report.celery.telegram_sent == 0
    assert first_report.celery.duplicate_count == retry_report.celery.duplicate_count == 0
    serialized = json.dumps(retry_report.to_dict())
    assert "api_key" not in serialized.lower()
    assert "telegram_bot_token" not in serialized.lower()
