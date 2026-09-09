import sqlite3
from pathlib import Path

import redis
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agent.engine import AgentEngine
from src.agent.executor import AgentExecutor
from src.agent.models import Observation
from src.config import settings
from src.repositories.agent_audit_repo import AgentAuditRepository
from src.repositories.article_repo import ArticleRepository
from src.repositories.run_repo import PipelineRunRepository

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentRequest(BaseModel):
    request: str


def observe_system() -> Observation:
    try:
        ArticleRepository(settings.database_url)
        db_ok = True
    except (sqlite3.Error, OSError):
        db_ok = False

    try:
        client = redis.from_url(settings.redis_url, socket_connect_timeout=1)
        client.ping()
        redis_ok = True
    except redis.RedisError:
        redis_ok = False

    db_path = PipelineRunRepository(settings.database_url).db_path if db_ok else ""
    active_runs = 0
    if db_path:
        with sqlite3.connect(db_path) as connection:
            row = connection.execute(
                "SELECT COUNT(*) FROM pipeline_runs WHERE status = 'running'"
            ).fetchone()
            active_runs = int(row[0]) if row else 0
    return Observation(db_ok=db_ok, redis_ok=redis_ok, active_run_count=active_runs)


@router.post("/run")
def run_agent(payload: AgentRequest):
    audit = AgentAuditRepository(settings.database_url)
    decision, verification = AgentEngine(audit).run(payload.request, observe_system())
    return {"decision": decision, "verification": verification}


@router.get("/audit/{correlation_id}")
def get_agent_audit(correlation_id: str):
    events = AgentAuditRepository(settings.database_url).list_for_correlation(correlation_id)
    return {"correlation_id": correlation_id, "events": events}


@router.post("/approve/{correlation_id}")
def approve_agent_action(correlation_id: str):
    audit = AgentAuditRepository(settings.database_url)
    events = audit.list_for_correlation(correlation_id)
    if not events:
        raise HTTPException(status_code=404, detail="Agent decision not found")
    if any(event["phase"] == "approval" for event in events):
        raise HTTPException(status_code=409, detail="Agent action was already approved")
    pending = any(
        event["phase"] == "act" and event["status"] == "pending_approval" for event in events
    )
    if not pending:
        raise HTTPException(status_code=409, detail="Agent decision is not awaiting approval")
    audit.record(correlation_id, "approval", "approved", "Explicit approval recorded")
    action_event = next(event for event in events if event["phase"] == "act")
    if action_event["message"].endswith("database_backup"):
        database_path = settings.database_url.replace("sqlite:///", "")
        try:
            target = AgentExecutor(database_path).execute_database_backup()
        except (OSError, sqlite3.Error) as exc:
            audit.record(correlation_id, "act", "failed", str(exc))
            audit.record(correlation_id, "verify", "failed", "Approved backup execution failed")
            return {"correlation_id": correlation_id, "status": "failed", "executed": False}
        audit.record(correlation_id, "act", "executed", f"Database backup created: {target}")
        audit.record(correlation_id, "verify", "passed", "Backup file created successfully")
        return {
            "correlation_id": correlation_id,
            "status": "completed",
            "executed": True,
            "backup_path": str(Path(target)),
        }
    return {"correlation_id": correlation_id, "status": "approved", "executed": False}
