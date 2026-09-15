import { useState } from "react";
import { Badge, Button, Card, Group, Text, TextInput } from "@mantine/core";
import { useMutation } from "@tanstack/react-query";
import { PageHeader } from "../components/ui/PageHeader";
import { approveAgent, runAgent } from "../features/agent/api";
import type { AgentRunResponse } from "../types/api";

export function AgentPage() {
  const [request, setRequest] = useState("backup");
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const run = useMutation({
    mutationFn: () => runAgent(request),
    onSuccess: async (response) => {
      setResult(response);
    },
  });
  const approve = useMutation({
    mutationFn: () => approveAgent(result!.decision.correlation_id),
    onSuccess: () => undefined,
  });

  const correlationId = result?.decision.correlation_id;
  return (
    <div>
      <PageHeader title="Assistant" description="A small helper for safe maintenance actions" />
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
              <Text size="sm" c="dimmed">The assistant will ask before making a protected change.</Text>
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
    </div>
  );
}
