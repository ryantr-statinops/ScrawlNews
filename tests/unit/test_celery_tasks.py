import json
import sqlite3
from unittest.mock import AsyncMock, patch

import pytest
from celery.exceptions import Retry

from src.config import settings
from src.models.article import Article
from src.models.run import PipelineRun
from src.models.summary import Summary
from src.repositories.article_repo import ArticleRepository
from src.repositories.run_repo import PipelineRunRepository
from src.repositories.summary_repo import SummaryRepository
from src.utils.errors import (
    ConfigError,
    MessengerError,
    NotFoundError,
    ScrawlerError,
    SynthesizerError,
)
from src.worker.tasks import pipeline_run


@pytest.fixture
def worker(monkeypatch):
    monkeypatch.setattr(settings, "telegram_enabled", True)
    pipeline_run.push_request(id="task-1", retries=0, called_directly=False)
    with patch("src.worker.tasks.ScrawlerService.execute", new_callable=AsyncMock) as fetch:
        with patch(
            "src.worker.tasks.SynthesizerService.execute", new_callable=AsyncMock
        ) as synthesize:
            with patch(
                "src.worker.tasks.MessengerService.execute", new_callable=AsyncMock
            ) as deliver:
                with patch.object(pipeline_run, "retry", side_effect=Retry()) as retry:
                    fetch.return_value = [
                        Article(id="a1", url="https://example.test", title="Title", category="tech")
                    ]
                    synthesize.return_value = [
                        Summary(id="s1", article_id="a1", summary_text="Summary", model_used="test")
                    ]
                    deliver.return_value = True
                    try:
                        yield fetch, synthesize, deliver, retry
                    finally:
                        pipeline_run.pop_request()


def saved_run():
    return PipelineRunRepository(settings.database_url).get("task-1")


def test_pipeline_run_success(worker):
    fetch, synthesize, deliver, retry = worker
    result = pipeline_run.run(fetch_limit=5, categories=["tech"])
    assert result == {
        "status": "success",
        "run_id": "task-1",
        "articles_fetched": 1,
        "summaries_generated": 1,
    }
    fetch.assert_awaited_once_with(limit=5, categories=["tech"])
    synthesize.assert_awaited_once_with(fetch.return_value, run_id="task-1")
    deliver.assert_awaited_once_with(synthesize.return_value)
    retry.assert_not_called()
    run = saved_run()
    assert run["status"] == "success"
    assert run["task_id"] == "task-1"
    assert run["telegram_sent"] == 1
    assert run["error"] is None
    assert run["started_at"] and run["finished_at"]
    assert ArticleRepository(settings.database_url).get_by_id("a1")["category"] == "tech"
    assert SummaryRepository(settings.database_url).get_by_id("s1")["summary_text"] == "Summary"


@pytest.mark.parametrize("dry_run,enabled", [(True, True), (False, False)])
def test_delivery_toggles(worker, monkeypatch, dry_run, enabled):
    monkeypatch.setattr(settings, "telegram_enabled", enabled)
    pipeline_run.run(dry_run=dry_run)
    worker[2].assert_not_awaited()
    assert saved_run()["status"] == "success"
    assert saved_run()["telegram_sent"] == 0


@pytest.mark.parametrize("duplicate", [True, False])
def test_no_new_articles_success(worker, duplicate):
    fetch, synthesize, deliver, retry = worker
    if duplicate:
        ArticleRepository(settings.database_url).save(fetch.return_value[0])
    else:
        fetch.return_value = []
    result = pipeline_run.run()
    assert result["articles_fetched"] == int(duplicate)
    assert result["summaries_generated"] == 0
    assert saved_run()["status"] == "success"
    synthesize.assert_not_awaited()
    deliver.assert_not_awaited()
    retry.assert_not_called()


@pytest.mark.parametrize("attempt", [0, 1, 2])
def test_transient_fetch_retry_and_resume(worker, attempt):
    fetch, synthesize, deliver, retry = worker
    pipeline_run.request.retries = attempt
    error = ScrawlerError("secret provider detail", retryable=True)
    fetch.side_effect = error
    with pytest.raises(Retry):
        pipeline_run.run(fetch_limit=7, dry_run=True, categories=["tech"])
    retry.assert_called_once()
    assert retry.call_args.kwargs["exc"] is error
    assert retry.call_args.kwargs["countdown"] == 2**attempt
    assert retry.call_args.kwargs["args"] == ()
    kwargs = json.loads(json.dumps(retry.call_args.kwargs["kwargs"]))
    assert kwargs == {
        "fetch_limit": 7,
        "dry_run": True,
        "categories": ["tech"],
        "_checkpoint": {"run_id": "task-1"},
    }
    run = saved_run()
    assert run["status"] == "running"
    assert run["finished_at"] is None
    assert (
        run["error"]
        == f"fetch: ScrawlerError: News source unavailable (retry {attempt + 1}/3 pending)"
    )
    synthesize.assert_not_awaited()
    deliver.assert_not_awaited()
    fetch.side_effect = None
    pipeline_run.request.retries += 1
    result = pipeline_run.run(**kwargs)
    assert result["run_id"] == "task-1"
    assert PipelineRunRepository(settings.database_url).count() == 1
    assert saved_run()["status"] == "success"
    assert saved_run()["error"] is None
    assert saved_run()["started_at"] == run["started_at"]


@pytest.mark.parametrize(
    "error",
    [
        ScrawlerError("permanent"),
        ConfigError("secret config"),
        TypeError("bug"),
        sqlite3.OperationalError("database is locked"),
    ],
)
def test_nonretryable_failure(worker, error):
    fetch, synthesize, deliver, retry = worker
    fetch.side_effect = error
    with pytest.raises(type(error)) as caught:
        pipeline_run.run()
    assert caught.value is error
    retry.assert_not_called()
    synthesize.assert_not_awaited()
    deliver.assert_not_awaited()
    run = saved_run()
    assert run["status"] == "failed"
    assert run["finished_at"]
    assert run["error"].startswith(f"fetch: {type(error).__name__}:")
    assert str(error) not in run["error"]


def test_retry_exhaustion_retains_original_failure(worker):
    fetch, _, _, retry = worker
    pipeline_run.request.retries = pipeline_run.max_retries
    error = ScrawlerError("offline", retryable=True)
    fetch.side_effect = error
    with pytest.raises(ScrawlerError) as caught:
        pipeline_run.run()
    assert caught.value is error
    retry.assert_not_called()
    assert saved_run()["status"] == "failed"
    assert saved_run()["error"] == "fetch: ScrawlerError: News source unavailable"
    assert saved_run()["finished_at"]


@pytest.mark.parametrize(
    "stage,error",
    [
        (1, SynthesizerError("offline", retryable=True)),
        (2, MessengerError("offline", retryable=True)),
    ],
)
def test_retry_resumes_saved_work(worker, stage, error):
    fetch, synthesize, deliver, retry = worker
    worker[stage].side_effect = error
    with pytest.raises(Retry):
        pipeline_run.run()
    kwargs = json.loads(json.dumps(retry.call_args.kwargs["kwargs"]))
    assert kwargs["_checkpoint"]["article_ids"] == ["a1"]
    if stage == 2:
        assert kwargs["_checkpoint"]["summary_ids"] == ["s1"]
        assert saved_run()["summaries_generated"] == 1
    assert saved_run()["articles_fetched"] == 1
    assert saved_run()["telegram_sent"] == 0
    worker[stage].side_effect = None
    pipeline_run.request.retries = 1
    result = pipeline_run.run(**kwargs)
    assert result["status"] == "success"
    assert result["articles_fetched"] == result["summaries_generated"] == 1
    fetch.assert_awaited_once()
    assert synthesize.await_count == (2 if stage == 1 else 1)
    assert deliver.await_count == (1 if stage == 1 else 2)
    assert ArticleRepository(settings.database_url).count() == 1
    assert SummaryRepository(settings.database_url).count() == 1
    assert PipelineRunRepository(settings.database_url).count() == 1
    assert saved_run()["telegram_sent"] == 1
    assert saved_run()["error"] is None


@pytest.mark.parametrize(
    "method,stage",
    [("ArticleRepository.save", "save articles"), ("SummaryRepository.save", "save summaries")],
)
def test_database_write_failure_is_not_success_or_retry(worker, method, stage):
    error = sqlite3.OperationalError("private database path")
    with patch(f"src.worker.tasks.{method}", side_effect=error):
        with pytest.raises(sqlite3.OperationalError) as caught:
            pipeline_run.run()
    assert caught.value is error
    worker[2].assert_not_awaited()
    worker[3].assert_not_called()
    run = saved_run()
    assert run["status"] == "failed"
    assert run["articles_fetched"] == 1
    assert run["summaries_generated"] == 0
    assert run["error"] == f"{stage}: OperationalError: Unexpected pipeline failure"


def test_run_creation_failure_stops_work(worker):
    with patch(
        "src.worker.tasks.PipelineRunRepository.create", side_effect=sqlite3.Error("write failed")
    ):
        with pytest.raises(sqlite3.Error, match="write failed"):
            pipeline_run.run()
    for service in worker[:3]:
        service.assert_not_awaited()
    worker[3].assert_not_called()
    assert saved_run() is None


def test_failure_recording_error_does_not_hide_original(worker, caplog):
    error = ScrawlerError("offline", retryable=True)
    worker[0].side_effect = error
    state_error = sqlite3.Error("state write failed")
    with patch(
        "src.worker.tasks.PipelineRunRepository.update_status", side_effect=[None, state_error]
    ):
        with pytest.raises(ScrawlerError) as caught:
            pipeline_run.run()
    assert caught.value is error
    assert caught.value.__cause__ is state_error
    assert "Unable to persist pipeline failure" in caplog.text
    worker[3].assert_not_called()


def test_retry_scheduling_failure_marks_run_failed(worker):
    worker[0].side_effect = ScrawlerError("offline", retryable=True)
    worker[3].side_effect = RuntimeError("broker secret")
    with pytest.raises(RuntimeError, match="broker secret"):
        pipeline_run.run()
    assert saved_run()["status"] == "failed"
    assert saved_run()["finished_at"]
    assert saved_run()["error"].endswith("retry scheduling failed")
    assert "broker secret" not in saved_run()["error"]


def test_direct_cli_failure_does_not_schedule_retry(worker):
    pipeline_run.request.called_directly = True
    worker[0].side_effect = ScrawlerError("offline", retryable=True)
    with pytest.raises(ScrawlerError):
        pipeline_run.run()
    worker[3].assert_not_called()
    assert saved_run()["status"] == "failed"


def test_false_delivery_is_failure(worker):
    worker[2].return_value = False
    with pytest.raises(MessengerError):
        pipeline_run.run()
    worker[3].assert_not_called()
    assert saved_run()["status"] == "failed"
    assert saved_run()["telegram_sent"] == 0


def test_missing_retry_data_fails_without_refetch(worker):
    repo = PipelineRunRepository(settings.database_url)
    repo.create(PipelineRun(id="task-1", status="running"))
    with pytest.raises(NotFoundError, match="Retry summary no longer exists"):
        pipeline_run.run(
            _checkpoint={"run_id": "task-1", "article_ids": ["a1"], "summary_ids": ["missing"]}
        )
    worker[0].assert_not_awaited()
    worker[1].assert_not_awaited()
    worker[2].assert_not_awaited()
    worker[3].assert_not_called()
    assert saved_run()["status"] == "failed"
