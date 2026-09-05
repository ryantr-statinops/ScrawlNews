import { useQuery } from "@tanstack/react-query";
import { Table } from "@mantine/core";
import { fetchRuns } from "../lib/api";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";
import type { PipelineRun } from "../types/api";

export function DeliveryPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["runs"], queryFn: fetchRuns });
  const runs: PipelineRun[] = data?.runs ?? [];

  return (
    <div>
      <PageHeader title="Delivery" description="Telegram delivery status per run (max 4096 chars split)" />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {!isLoading && !error && runs.length === 0 ? <EmptyState /> : null}
      {runs.length > 0 ? (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Run</Table.Th>
              <Table.Th>Telegram sent</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {runs.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>{r.id.slice(0, 8)}</Table.Td>
                <Table.Td>{r.telegram_sent ? "yes" : "no"}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      ) : null}
    </div>
  );
}
