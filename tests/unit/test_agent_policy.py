from src.agent.models import Observation
from src.agent.policy import AgentPolicy


def healthy_observation(**overrides):
    values = {"db_ok": True, "redis_ok": True}
    values.update(overrides)
    return Observation(**values)


def test_policy_allows_database_backup():
    decision = AgentPolicy().decide("backup", healthy_observation())

    assert decision.status == "ready"
    assert decision.action is not None
    assert decision.action.kind == "database_backup"
    assert decision.action.dry_run is True


def test_policy_allows_pipeline_dry_run():
    decision = AgentPolicy().decide("refresh", healthy_observation())

    assert decision.status == "ready"
    assert decision.action is not None
    assert decision.action.kind == "pipeline_dry_run"


def test_policy_blocks_unknown_request():
    decision = AgentPolicy().decide("delete everything", healthy_observation())

    assert decision.status == "blocked"
    assert decision.action is None


def test_policy_blocks_unhealthy_system():
    decision = AgentPolicy().decide("backup", healthy_observation(redis_ok=False))

    assert decision.status == "blocked"
    assert decision.action is None


def test_policy_blocks_when_pipeline_is_active():
    decision = AgentPolicy().decide("refresh", healthy_observation(active_run_count=1))

    assert decision.status == "blocked"
    assert decision.action is None
