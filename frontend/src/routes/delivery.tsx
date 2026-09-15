import { useQuery } from "@tanstack/react-query";
import { Table, SimpleGrid, Card, Text } from "@mantine/core";
import { fetchRuns } from "../lib/api";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";
import { StatusBadge } from "../components/ui/StatusBadge";
import type { PipelineRun } from "../types/api";

export function DeliveryPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["runs"], queryFn: fetchRuns });
  const runs: PipelineRun[] = data?.runs ?? [];
  const sent = runs.filter((r) => r.telegram_sent === 1).length;
  const failed = runs.filter((r) => r.status === "failed").length;

  return (
    <div>
      <PageHeader title="Telegram" description="Your digest delivery status" />
      <SimpleGrid cols={{ base: 1, sm: 3 }} mb="md">
        <Card shadow="sm" padding="md">
          <Text size="xs" c="dimmed">Delivery attempts</Text>
          <Text size="xl" fw={600}>{runs.length}</Text>
        </Card>
        <Card shadow="sm" padding="md">
          <Text size="xs" c="dimmed">Delivered</Text>
          <Text size="xl" fw={600} c="green">{sent}</Text>
        </Card>
        <Card shadow="sm" padding="md">
          <Text size="xs" c="dimmed">Needs attention</Text>
          <Text size="xl" fw={600} c="red">{failed}</Text>
        </Card>
      </SimpleGrid>
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {!isLoading && !error && runs.length === 0 ? <EmptyState message="No Telegram deliveries yet" /> : null}
      {runs.length > 0 ? (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Delivery</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Telegram</Table.Th>
              <Table.Th>Started</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {runs.map((r, index) => (
              <Table.Tr key={r.id}>
                <Table.Td>#{runs.length - index}</Table.Td>
                <Table.Td>
                  <StatusBadge status={r.status} />
                </Table.Td>
                <Table.Td>{r.telegram_sent ? "Delivered" : "Not delivered"}</Table.Td>
                <Table.Td>{r.started_at ? new Date(r.started_at).toLocaleString() : "-"}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      ) : null}
    </div>
  );
}
