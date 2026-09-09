from src.repositories.agent_audit_repo import AgentAuditRepository


def test_agent_audit_events_are_recorded_in_order(tmp_path):
    repository = AgentAuditRepository(f"sqlite:///{tmp_path / 'agent.db'}")

    first_id = repository.record("corr-1", "observe", "ok", "System is healthy")
    second_id = repository.record("corr-1", "decide", "ready", "Backup allowed")
    repository.record("other", "observe", "ok", "Ignored for this correlation")

    events = repository.list_for_correlation("corr-1")

    assert [event["id"] for event in events] == [first_id, second_id]
    assert [event["phase"] for event in events] == ["observe", "decide"]
    assert events[1]["status"] == "ready"
