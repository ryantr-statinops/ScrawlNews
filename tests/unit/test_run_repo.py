from src.models.run import PipelineRun


def test_create_and_get(run_repo):
    run = PipelineRun(id="run-1", status="pending")
    run_repo.create(run)
    retrieved = run_repo.get("run-1")
    assert retrieved is not None
    assert retrieved["status"] == "pending"


def test_list_recent(run_repo):
    run1 = PipelineRun(id="run-1", status="success")
    run2 = PipelineRun(id="run-2", status="failed")
    run_repo.create(run1)
    run_repo.create(run2)
    recent = run_repo.list_recent(limit=10)
    assert len(recent) >= 2
    ids = [r["id"] for r in recent]
    assert "run-1" in ids
    assert "run-2" in ids


def test_update_status(run_repo):
    run = PipelineRun(id="run-1", status="pending")
    run_repo.create(run)
    run_repo.update_status("run-1", "running", task_id="task-123")
    updated = run_repo.get("run-1")
    assert updated["status"] == "running"
    assert updated["task_id"] == "task-123"


def test_update_status_multiple_fields(run_repo):
    run = PipelineRun(id="run-1", status="running", articles_fetched=0)
    run_repo.create(run)
    run_repo.update_status(
        "run-1",
        "success",
        articles_fetched=20,
        summaries_generated=18,
        telegram_sent=1,
    )
    updated = run_repo.get("run-1")
    assert updated["status"] == "success"
    assert updated["articles_fetched"] == 20
    assert updated["summaries_generated"] == 18
    assert updated["telegram_sent"] == 1


def test_count(run_repo):
    assert run_repo.count() == 0
    run = PipelineRun(id="run-1", status="pending")
    run_repo.create(run)
    assert run_repo.count() == 1


def test_get_not_found(run_repo):
    result = run_repo.get("nonexistent")
    assert result is None
