"""Data contracts shared by the Agent v1 observe/decide/act loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

AgentStatus = Literal["ready", "pending_approval", "blocked", "completed", "failed"]
ActionKind = Literal["pipeline_dry_run", "database_backup"]


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class Observation:
    """Read-only state presented to the policy engine."""

    db_ok: bool
    redis_ok: bool
    latest_run_status: str | None = None
    active_run_count: int = 0

    @property
    def healthy(self) -> bool:
        return self.db_ok and self.redis_ok


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    dry_run: bool = True
    parameters: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Decision:
    status: AgentStatus
    reason: str
    action: Action | None = None
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class Verification:
    status: Literal["passed", "failed", "skipped"]
    message: str
    correlation_id: str
    verified_at: datetime = field(default_factory=utc_now)
