import type { AgentAuditEvent, AgentRunResponse } from "../../types/api";

export async function runAgent(request: string): Promise<AgentRunResponse> {
  const response = await fetch("/api/agent/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request }),
  });
  if (!response.ok) throw new Error(`Agent request failed: ${response.status}`);
  return response.json();
}

export async function approveAgent(correlationId: string): Promise<{
  correlation_id: string;
  status: string;
  executed: boolean;
  backup_path?: string;
}> {
  const response = await fetch(`/api/agent/approve/${correlationId}`, { method: "POST" });
  if (!response.ok) throw new Error(`Agent approval failed: ${response.status}`);
  return response.json();
}

export async function fetchAgentAudit(correlationId: string): Promise<AgentAuditEvent[]> {
  const response = await fetch(`/api/agent/audit/${correlationId}`);
  if (!response.ok) throw new Error(`Agent audit request failed: ${response.status}`);
  const body: { events: AgentAuditEvent[] } = await response.json();
  return body.events;
}
