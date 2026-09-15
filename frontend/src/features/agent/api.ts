import type { AgentAuditEvent, AgentRunResponse } from "../../types/api";
import { requestJson } from "../../lib/api";

export async function runAgent(request: string): Promise<AgentRunResponse> {
  return requestJson<AgentRunResponse>("/api/agent/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request }),
  });
}

export async function approveAgent(correlationId: string): Promise<{
  correlation_id: string;
  status: string;
  executed: boolean;
  backup_path?: string;
}> {
  return requestJson(`/api/agent/approve/${encodeURIComponent(correlationId)}`, { method: "POST" });
}

export async function fetchAgentAudit(correlationId: string): Promise<AgentAuditEvent[]> {
  const body = await requestJson<{ events: AgentAuditEvent[] }>(
    `/api/agent/audit/${encodeURIComponent(correlationId)}`,
  );
  return body.events;
}
