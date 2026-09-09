import { useState } from "react";
import { Badge, Button, Card, Group, Table, Text, TextInput } from "@mantine/core";
import { useMutation } from "@tanstack/react-query";
import { PageHeader } from "../components/ui/PageHeader";
import { approveAgent, fetchAgentAudit, runAgent } from "../features/agent/api";
import type { AgentAuditEvent, AgentRunResponse } from "../types/api";

export function AgentPage() {
  const [request, setRequest] = useState("backup");
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [events, setEvents] = useState<AgentAuditEvent[]>([]);
  const run = useMutation({
    mutationFn: () => runAgent(request),
    onSuccess: async (response) => {
      setResult(response);
      setEvents(await fetchAgentAudit(response.decision.correlation_id));
    },
  });
  const approve = useMutation({
    mutationFn: () => approveAgent(result!.decision.correlation_id),
    onSuccess: async () => {
      setEvents(await fetchAgentAudit(result!.decision.correlation_id));
    },
  });

  const correlationId = result?.decision.correlation_id;
  return (
    <div>
      <PageHeader title="Agent" description="Deterministic operator with approval and audit trail" />
      <Card withBorder mb="md">
        <Group align="end">
          <TextInput
            label="Request"
            value={request}
            onChange={(event) => setRequest(event.currentTarget.value)}
            placeholder="backup or refresh"
            style={{ flex: 1 }}
          />
          <Button onClick={() => run.mutate()} loading={run.isPending} disabled={!request.trim()}>
            Ask Agent
          </Button>
        </Group>
      </Card>
      {result ? (
        <Card withBorder mb="md">
          <Group justify="space-between">
            <div>
              <Text fw={600}>{result.decision.reason}</Text>
              <Text size="sm" c="dimmed">Correlation: {correlationId}</Text>
            </div>
            <Badge color={result.decision.status === "pending_approval" ? "yellow" : "gray"}>
              {result.decision.status}
            </Badge>
          </Group>
          {result.decision.status === "pending_approval" ? (
            <Button mt="md" onClick={() => approve.mutate()} loading={approve.isPending}>
              Approve action
            </Button>
          ) : null}
        </Card>
      ) : null}
      {events.length ? (
        <Table striped withTableBorder>
          <Table.Thead><Table.Tr><Table.Th>Phase</Table.Th><Table.Th>Status</Table.Th><Table.Th>Message</Table.Th></Table.Tr></Table.Thead>
          <Table.Tbody>
            {events.map((event) => (
              <Table.Tr key={event.id}>
                <Table.Td>{event.phase}</Table.Td>
                <Table.Td>{event.status}</Table.Td>
                <Table.Td>{event.message}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      ) : null}
    </div>
  );
}
