import sqlite3

from src.repositories.telemetry_repo import TelemetryRepository


def test_telemetry_repository_records_all_event_types(temp_db):
    repo = TelemetryRepository(f"sqlite:///{temp_db}")
    assert repo.record_stage(run_id="r1", stage="fetch", status="success") > 0
    assert repo.record_source_fetch(
        run_id="r1", source_id="s1", source_name="Source", status="success",
        category="technology", country="VN",
    ) > 0
    assert repo.record_llm_usage(
        run_id="r1", operation="article_summary", provider="openrouter",
        model="model", status="success", total_tokens=10,
    ) > 0
    with sqlite3.connect(repo.db_path) as conn:
        source = conn.execute(
            "SELECT category, country FROM source_fetch_events"
        ).fetchone()
    assert source == ("technology", "VN")


def test_telemetry_cleanup_removes_only_expired_events(temp_db):
    repo = TelemetryRepository(f"sqlite:///{temp_db}")
    repo.record_stage(
        run_id="old", stage="fetch", status="success",
        started_at="2020-01-01T00:00:00", finished_at="2020-01-01T00:00:01",
    )
    repo.record_stage(run_id="new", stage="fetch", status="success")
    assert repo.cleanup(30) == 1
