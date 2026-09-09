from src.agent.engine import AgentEngine
from src.agent.models import Observation
from src.repositories.agent_audit_repo import AgentAuditRepository


def test_engine_records_complete_dry_run_lifecycle(tmp_path):
    repository = AgentAuditRepository(f"sqlite:///{tmp_path / 'agent.db'}")
    engine = AgentEngine(repository)

    decision, verification = engine.run("backup", Observation(db_ok=True, redis_ok=True))

    assert decision.status == "ready"
    assert verification.status == "skipped"
    events = repository.list_for_correlation(decision.correlation_id)
    assert [event["phase"] for event in events] == ["observe", "decide", "act", "verify"]
    assert events[2]["status"] == "skipped"


def test_engine_does_not_act_when_policy_blocks(tmp_path):
    repository = AgentAuditRepository(f"sqlite:///{tmp_path / 'agent.db'}")
    engine = AgentEngine(repository)

    decision, verification = engine.run(
        "delete everything", Observation(db_ok=True, redis_ok=True)
    )

    assert decision.status == "blocked"
    assert verification.status == "skipped"
    events = repository.list_for_correlation(decision.correlation_id)
    assert [event["phase"] for event in events] == ["observe", "decide", "verify"]
