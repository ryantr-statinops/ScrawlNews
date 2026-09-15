"""Safe, lifecycle-focused comparison helpers for Celery and Dagster runs.

The comparison deliberately records identities, counts and statuses only. It never
serializes article content, summaries, digests or runtime configuration secrets.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from time import perf_counter

from src.models.article import Article
from src.models.digest import Digest
from src.models.summary import Summary


@dataclass(frozen=True)
class PipelineInput:
    fetch_limit: int
    categories: tuple[str, ...]
    telegram_enabled: bool = False


@dataclass(frozen=True)
class PipelineExecution:
    articles: tuple[Article, ...] = ()
    summaries: tuple[Summary, ...] = ()
    digests: tuple[Digest, ...] = ()
    duplicate_count: int = 0
    fallback_count: int = 0
    error_stage: str | None = None
    telegram_sent: int = 0
    domain_db_mutated: bool = False
    stage_status: tuple[tuple[str, str], ...] = ()
    runtime_ms: int = 0


@dataclass(frozen=True)
class PipelineSnapshot:
    article_ids: tuple[str, ...]
    article_urls: tuple[str, ...]
    article_count: int
    duplicate_count: int
    summary_count: int
    digest_count: int
    categories: tuple[str, ...]
    fallback_count: int
    error_stage: str | None
    telegram_sent: int
    domain_db_mutated: bool
    stage_status: tuple[tuple[str, str], ...]
    runtime_ms: int


@dataclass(frozen=True)
class ComparisonResult:
    passed: bool
    differences: tuple[str, ...]


@dataclass(frozen=True)
class ComparisonReport:
    input: PipelineInput
    celery: PipelineSnapshot
    dagster: PipelineSnapshot
    parity: ComparisonResult

    def to_dict(self) -> dict:
        """Return a report-safe structure without content or credentials."""
        return {
            "input": asdict(self.input),
            "celery": asdict(self.celery),
            "dagster": asdict(self.dagster),
            "parity": asdict(self.parity),
        }


def snapshot_execution(execution: PipelineExecution) -> PipelineSnapshot:
    articles = tuple(execution.articles)
    return PipelineSnapshot(
        article_ids=tuple(sorted(article.id for article in articles)),
        article_urls=tuple(sorted(article.url for article in articles)),
        article_count=len(articles),
        duplicate_count=execution.duplicate_count,
        summary_count=len(execution.summaries),
        digest_count=len(execution.digests),
        categories=tuple(sorted({digest.category for digest in execution.digests})),
        fallback_count=execution.fallback_count
        or sum(summary.model_used == "fallback" for summary in execution.summaries),
        error_stage=execution.error_stage,
        telegram_sent=execution.telegram_sent,
        domain_db_mutated=execution.domain_db_mutated,
        stage_status=execution.stage_status,
        runtime_ms=execution.runtime_ms,
    )


def compare_snapshots(celery: PipelineSnapshot, dagster: PipelineSnapshot) -> ComparisonResult:
    comparable_fields = (
        "article_ids",
        "article_urls",
        "article_count",
        "duplicate_count",
        "summary_count",
        "digest_count",
        "categories",
        "fallback_count",
        "error_stage",
        "telegram_sent",
        "domain_db_mutated",
        "stage_status",
    )
    differences = tuple(
        f"{field}: celery={getattr(celery, field)!r}, dagster={getattr(dagster, field)!r}"
        for field in comparable_fields
        if getattr(celery, field) != getattr(dagster, field)
    )
    return ComparisonResult(passed=not differences, differences=differences)


Runner = Callable[[PipelineInput], PipelineExecution]


def run_comparison(
    pipeline_input: PipelineInput,
    celery_runner: Runner,
    dagster_runner: Runner,
) -> ComparisonReport:
    """Run both adapters against the same input and compare their lifecycles."""
    celery_started = perf_counter()
    celery_execution = celery_runner(pipeline_input)
    celery_elapsed = round((perf_counter() - celery_started) * 1000)
    dagster_started = perf_counter()
    dagster_execution = dagster_runner(pipeline_input)
    dagster_elapsed = round((perf_counter() - dagster_started) * 1000)

    celery_snapshot = snapshot_execution(
        _with_runtime(celery_execution, celery_execution.runtime_ms or celery_elapsed)
    )
    dagster_snapshot = snapshot_execution(
        _with_runtime(dagster_execution, dagster_execution.runtime_ms or dagster_elapsed)
    )
    return ComparisonReport(
        input=pipeline_input,
        celery=celery_snapshot,
        dagster=dagster_snapshot,
        parity=compare_snapshots(celery_snapshot, dagster_snapshot),
    )


def _with_runtime(execution: PipelineExecution, runtime_ms: int) -> PipelineExecution:
    values = asdict(execution)
    values["runtime_ms"] = runtime_ms
    values["articles"] = execution.articles
    values["summaries"] = execution.summaries
    values["digests"] = execution.digests
    return PipelineExecution(**values)
