import { useQuery } from "@tanstack/react-query";
import { Card, Text, Code, Table } from "@mantine/core";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { useLogStream } from "../lib/sse";
import { fetchRuns, requestJson } from "../lib/api";
import type { HealthResponse, PipelineRun } from "../types/api";

const fetchHealth = () => requestJson<HealthResponse>("/health");

export function HealthPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["health"], queryFn: fetchHealth });
  const runsQuery = useQuery({
    queryKey: ["runs"],
    queryFn: async () => {
      return fetchRuns();
    },
  });
  const failed = (runsQuery.data?.runs ?? []).filter((r: PipelineRun) => r.status === "failed");
  const logs = useLogStream();

  return (
    <div>
      <PageHeader title="Health" description="Liveness + readiness (DB + Redis)" />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {data ? (
        <Card shadow="sm" mb="md">
          <Text>
            status: {data.status} · db: {data.db} · redis: {data.redis}
          </Text>
        </Card>
      ) : null}
      <Card shadow="sm" mb="md">
        <Text fw={600} mb="xs">
          Error board ({failed.length} failed runs)
        </Text>
        {failed.length > 0 ? (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Run</Table.Th>
                <Table.Th>Error</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {failed.map((r: PipelineRun) => (
                <Table.Tr key={r.id}>
                  <Table.Td style={{ fontFamily: "monospace" }}>{r.id.slice(0, 8)}</Table.Td>
                  <Table.Td>{r.error ?? "-"}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        ) : (
          <Text size="sm" c="dimmed">
            No failures
          </Text>
        )}
      </Card>
      <Card shadow="sm">
        <Text fw={600} mb="xs">
          Live logs (SSE)
        </Text>
        <Code block>
          {logs.length > 0 ? logs.join("\n") : "waiting for stream..."}
        </Code>
      </Card>
    </div>
  );
}
