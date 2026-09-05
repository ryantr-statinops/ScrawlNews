import { useQuery } from "@tanstack/react-query";
import { Table } from "@mantine/core";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";
import type { Summary } from "../types/api";

async function fetchSummaries() {
  const res = await fetch("/api/summaries?limit=20");
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json();
}

export function SummariesPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["summaries"], queryFn: fetchSummaries });
  const summaries: Summary[] = data?.summaries ?? [];

  return (
    <div>
      <PageHeader title="Summaries" description="Side-by-side article vs summary" />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {!isLoading && !error && summaries.length === 0 ? <EmptyState /> : null}
      {summaries.length > 0 ? (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Article</Table.Th>
              <Table.Th>Summary</Table.Th>
              <Table.Th>Model</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {summaries.map((s) => (
              <Table.Tr key={s.id}>
                <Table.Td>{s.article_id.slice(0, 8)}</Table.Td>
                <Table.Td>{s.summary_text.slice(0, 120)}</Table.Td>
                <Table.Td>{s.model_used}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      ) : null}
    </div>
  );
}
