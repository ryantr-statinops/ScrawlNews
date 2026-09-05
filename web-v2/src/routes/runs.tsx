import { Button, Table, Group } from "@mantine/core";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchRuns, triggerRun } from "../lib/api";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";
import { StatusBadge } from "../components/ui/StatusBadge";
import type { PipelineRun } from "../types/api";

export function RunsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ["runs"],
    queryFn: fetchRuns,
  });
  const trigger = useMutation({
    mutationFn: () => triggerRun(20),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["runs"] }),
  });

  const runs: PipelineRun[] = data?.runs ?? [];

  return (
    <div>
      <Group justify="space-between" mb="md">
        <PageHeader title="Runs" description="Pipeline runs triggered via Celery" />
        <Button onClick={() => trigger.mutate()} loading={trigger.isPending}>
          Run Now
        </Button>
      </Group>
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {!isLoading && !error && runs.length === 0 ? <EmptyState message="No runs yet" /> : null}
      {runs.length > 0 ? (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Articles</Table.Th>
              <Table.Th>Summaries</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {runs.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>{r.id.slice(0, 8)}</Table.Td>
                <Table.Td>
                  <StatusBadge status={r.status} />
                </Table.Td>
                <Table.Td>{r.articles_fetched}</Table.Td>
                <Table.Td>{r.summaries_generated}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      ) : null}
    </div>
  );
}
