import sqlite3
from datetime import UTC, datetime

import pytest

from src.services.analytics import AnalyticsService, comparison, percentile


def _service(tmp_path) -> AnalyticsService:
    return AnalyticsService(
        f"sqlite:///{tmp_path}/analytics.db",
        now=datetime(2026, 9, 9, 12, 0, tzinfo=UTC),
    )


def test_periods_are_adjacent_and_respect_configured_timezone(tmp_path):
    service = _service(tmp_path)
    with sqlite3.connect(service.db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('schedule_timezone', 'Asia/Ho_Chi_Minh')"
        )
        conn.commit()

    period = service.period("24h")

    assert period.timezone == "Asia/Ho_Chi_Minh"
    assert period.previous_end == period.current_start
    assert period.current_end - period.current_start == period.previous_end - period.previous_start


def test_invalid_window_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="Unsupported analytics window"):
        _service(tmp_path).period("90d")


def test_comparison_and_percentile_handle_empty_baselines():
    assert comparison(8, 0) == {
        "current": 8,
        "previous": 0,
        "delta": 8,
        "delta_percent": None,
    }
    assert percentile([], 0.95) == 0.0
    assert percentile([10, 20, 30, 40], 0.95) == 40


def test_overview_compares_current_and_previous_periods(tmp_path):
    service = _service(tmp_path)
    with sqlite3.connect(service.db_path) as conn:
        conn.executemany(
            """INSERT INTO articles
            (id, url, title, source, category, fetched_at, published_at, summarized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("current-1", "https://a/1", "One", "Source A", "technology", "2026-09-09T11:00:00", "2026-09-09T10:30:00", 1),
                ("current-2", "https://a/2", "Two", "Source B", "science", "2026-09-09T10:00:00", None, 0),
                ("previous-1", "https://a/3", "Three", "Source A", "technology", "2026-09-08T11:00:00", None, 0),
            ],
        )
        conn.execute(
            "INSERT INTO summaries (id, article_id, summary_text, model_used, created_at) "
            "VALUES ('summary-1', 'current-1', 'Summary', 'model-a', '2026-09-09T11:05:00')"
        )
        conn.executemany(
            """INSERT INTO pipeline_runs
            (id, status, articles_fetched, started_at, finished_at) VALUES (?, ?, ?, ?, ?)""",
            [
                ("run-current", "success", 2, "2026-09-09T09:00:00", "2026-09-09T09:01:00"),
                ("run-previous", "failed", 1, "2026-09-08T09:00:00", "2026-09-08T09:01:00"),
            ],
        )
        conn.execute(
            """INSERT INTO source_fetch_events
            (run_id, source_id, source_name, status, fetched_count, new_count,
             duplicate_count, latency_ms, occurred_at)
            VALUES ('run-current', 'source-a', 'Source A', 'success', 2, 2, 0, 100, '2026-09-09T09:00:00')"""
        )
        conn.execute(
            """INSERT INTO llm_usage_events
            (run_id, operation, provider, model, input_tokens, output_tokens,
             total_tokens, latency_ms, status, occurred_at)
            VALUES ('run-current', 'article_summary', 'openrouter', 'model-a',
                    100, 20, 120, 300, 'success', '2026-09-09T09:00:00')"""
        )
        conn.commit()

    result = service.overview("24h")

    assert result["kpis"]["articles"] == {
        "current": 2,
        "previous": 1,
        "delta": 1,
        "delta_percent": 100.0,
    }
    assert result["kpis"]["summary_coverage"]["current"] == 50.0
    assert result["kpis"]["pipeline_success_rate"]["current"] == 100.0
    assert result["kpis"]["total_tokens"]["current"] == 120
    assert result["kpis"]["active_sources"]["current"] == 1


def test_pipeline_sources_and_ai_usage_aggregate_telemetry(tmp_path):
    service = _service(tmp_path)
    with sqlite3.connect(service.db_path) as conn:
        conn.execute(
            """INSERT INTO pipeline_runs
            (id, status, articles_fetched, started_at, finished_at)
            VALUES ('run-1', 'success', 4, '2026-09-09 11:00:00', '2026-09-09 11:00:10')"""
        )
        conn.executemany(
            """INSERT INTO pipeline_stage_events
            (run_id, stage, status, duration_ms, item_count, error_class, started_at, finished_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("run-1", "fetch", "success", 5000, 4, None, "2026-09-09T11:00:00", "2026-09-09T11:00:05"),
                ("run-1", "digest", "failed", 2000, 0, "TimeoutError", "2026-09-09T11:00:05", "2026-09-09T11:00:07"),
            ],
        )
        conn.execute(
            """INSERT INTO source_fetch_events
            (run_id, source_id, source_name, status, fetched_count, new_count,
             duplicate_count, latency_ms, occurred_at)
            VALUES ('run-1', 'source-a', 'Source A', 'success', 5, 4, 1, 500, '2026-09-09T11:00:00')"""
        )
        conn.executemany(
            """INSERT INTO llm_usage_events
            (run_id, operation, provider, model, input_tokens, output_tokens,
             total_tokens, latency_ms, status, occurred_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("run-1", "article_summary", "openrouter", "model-a", 100, 20, 120, 300, "success", "2026-09-09T11:00:00"),
                ("run-1", "topic_digest", "openrouter", "model-a", 50, 10, 60, 700, "failed", "2026-09-09T11:00:01"),
            ],
        )
        conn.commit()

    pipeline = service.pipeline("24h")
    sources = service.sources("24h")
    usage = service.ai_usage("24h")

    assert pipeline["kpis"]["throughput"]["current"] == 4
    assert pipeline["kpis"]["median_duration_seconds"]["current"] == 10.0
    assert pipeline["errors"] == [
        {"stage": "digest", "error_class": "TimeoutError", "count": 1}
    ]
    assert sources["sources"][0]["duplicate_rate"] == 20.0
    assert usage["kpis"]["total_tokens"]["current"] == 180
    assert usage["kpis"]["failure_rate"]["current"] == 50.0
    assert usage["operations"][0]["operation"] == "article_summary"


def test_drilldown_limits_records_and_rejects_unknown_kind(tmp_path):
    service = _service(tmp_path)
    with sqlite3.connect(service.db_path) as conn:
        conn.execute(
            """INSERT INTO pipeline_runs
            (id, status, started_at, finished_at)
            VALUES ('run-1', 'success', '2026-09-09T11:00:00', '2026-09-09T11:00:01')"""
        )
        conn.commit()

    result = service.drilldown("runs", "24h", limit=500)

    assert result["kind"] == "runs"
    assert [record["id"] for record in result["records"]] == ["run-1"]
    with pytest.raises(ValueError, match="Unsupported drilldown kind"):
        service.drilldown("unknown", "24h")
