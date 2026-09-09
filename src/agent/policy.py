"""Deterministic safety policy for Agent v1."""

from __future__ import annotations

from src.agent.models import Action, Decision, Observation


class AgentPolicy:
    """Translate an operator request and an observation into a safe decision."""

    def decide(self, request: str, observation: Observation) -> Decision:
        normalized = request.strip().lower()
        if not observation.healthy:
            return Decision(status="blocked", reason="Database or Redis health check failed")
        if observation.active_run_count:
            return Decision(status="blocked", reason="A pipeline run is already active")

        if normalized in {"backup", "database backup", "sao lưu", "sao luu"}:
            action = Action(kind="database_backup")
            return Decision(status="ready", reason="Database backup is allowed by policy", action=action)

        if normalized in {"run", "pipeline", "refresh", "dry run", "chạy pipeline", "chay pipeline"}:
            action = Action(kind="pipeline_dry_run")
            return Decision(status="ready", reason="Pipeline dry-run is allowed by policy", action=action)

        return Decision(status="blocked", reason="Request is outside the Agent v1 allowlist")
