from src.dagster_project.comparison import (
    PipelineExecution,
    PipelineInput,
    compare_snapshots,
    run_comparison,
    snapshot_execution,
)


def test_snapshot_contains_only_lifecycle_fields(sample_articles):
    execution = PipelineExecution(articles=tuple(sample_articles), fallback_count=2)

    snapshot = snapshot_execution(execution)

    assert snapshot.article_ids == tuple(sorted(article.id for article in sample_articles))
    assert snapshot.article_urls == tuple(sorted(article.url for article in sample_articles))
    assert snapshot.article_count == 3
    assert snapshot.summary_count == 0
    assert snapshot.digest_count == 0
    assert snapshot.fallback_count == 2


def test_identical_lifecycles_have_parity(sample_articles):
    execution = PipelineExecution(
        articles=tuple(sample_articles),
        duplicate_count=1,
        fallback_count=3,
        telegram_sent=0,
        domain_db_mutated=False,
        stage_status=(("fetch", "success"), ("digest", "success")),
    )

    result = compare_snapshots(snapshot_execution(execution), snapshot_execution(execution))

    assert result.passed is True
    assert result.differences == ()


def test_different_lifecycle_reports_field_level_difference(sample_articles):
    celery = snapshot_execution(PipelineExecution(articles=tuple(sample_articles)))
    dagster = snapshot_execution(
        PipelineExecution(articles=tuple(sample_articles[:2]), domain_db_mutated=True)
    )

    result = compare_snapshots(celery, dagster)

    assert result.passed is False
    assert any(item.startswith("article_ids:") for item in result.differences)
    assert any(item.startswith("domain_db_mutated:") for item in result.differences)


def test_runner_uses_same_input_and_ignores_runtime_for_parity(sample_articles):
    pipeline_input = PipelineInput(fetch_limit=2, categories=("technology",))
    received: list[PipelineInput] = []

    def runner(input_value):
        received.append(input_value)
        return PipelineExecution(articles=tuple(sample_articles), runtime_ms=42)

    report = run_comparison(pipeline_input, runner, runner)

    assert received == [pipeline_input, pipeline_input]
    assert report.parity.passed is True
    assert report.celery.runtime_ms == 42
    assert report.dagster.runtime_ms == 42
    assert report.to_dict()["input"]["telegram_enabled"] is False
