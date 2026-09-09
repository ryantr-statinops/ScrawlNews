"""Orchestrate the safe, auditable Agent v1 lifecycle."""

from __future__ import annotations

from src.agent.models import Decision, Observation, Verification
from src.agent.policy import AgentPolicy
from src.repositories.agent_audit_repo import AgentAuditRepository


class AgentEngine:
    def __init__(self, audit_repository: AgentAuditRepository, policy: AgentPolicy | None = None):
        self.audit_repository = audit_repository
        self.policy = policy or AgentPolicy()

    def run(self, request: str, observation: Observation) -> tuple[Decision, Verification]:
        decision = self.policy.decide(request, observation)
        correlation_id = decision.correlation_id
        self.audit_repository.record(
            correlation_id, "observe", "ok" if observation.healthy else "failed", self._observation_message(observation)
        )
        self.audit_repository.record(correlation_id, "decide", decision.status, decision.reason)

        if decision.status != "ready" or decision.action is None:
            verification = Verification("skipped", "No action was approved", correlation_id)
            self.audit_repository.record(correlation_id, "verify", verification.status, verification.message)
            return decision, verification

        action_message = f"Dry-run: {decision.action.kind} was not executed"
        self.audit_repository.record(correlation_id, "act", "skipped", action_message)
        verification = Verification("skipped", "Action execution awaits explicit approval", correlation_id)
        self.audit_repository.record(correlation_id, "verify", verification.status, verification.message)
        return decision, verification

    @staticmethod
    def _observation_message(observation: Observation) -> str:
        return (
            f"db_ok={observation.db_ok}, redis_ok={observation.redis_ok}, "
            f"active_run_count={observation.active_run_count}"
        )
