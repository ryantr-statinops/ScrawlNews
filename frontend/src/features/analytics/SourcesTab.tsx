import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge, Card, Group, Progress, Select, SimpleGrid, Table, Text, Title } from "@mantine/core";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { analyticsApi } from "./api";
import { AnalyticsDrawer, type DrilldownSelection } from "./AnalyticsDrawer";
import type { AnalyticsFiltersState } from "./types";

export function SourcesTab({ filters }: { filters: AnalyticsFiltersState }) {
  const [country, setCountry] = useState<string | null>(null);
  const [selection, setSelection] = useState<DrilldownSelection | null>(null);
  const query = useQuery({ queryKey: ["analytics", "sources", filters, country], queryFn: () => analyticsApi.sources(filters, country) });
  if (query.isLoading) return <LoadingState />;
  if (query.error) return <ErrorState message={(query.error as Error).message} />;
  if (!query.data) return null;
  const sources = query.data.sources;
  const countries = Array.from(new Set(sources.map((source) => source.country).filter(Boolean))) as string[];
  const fetched = sources.reduce((sum, source) => sum + source.fetched, 0);
  const added = sources.reduce((sum, source) => sum + source.new, 0);
  const duplicates = sources.reduce((sum, source) => sum + source.duplicates, 0);
  const fetches = sources.reduce((sum, source) => sum + source.fetches, 0);
  const weightedSuccess = fetches ? sources.reduce((sum, source) => sum + source.success_rate * source.fetches, 0) / fetches : 0;

  return (
    <>
      <Group justify="flex-end" mb="md"><Select label="Country" placeholder="All countries" clearable value={country} data={countries} onChange={setCountry} w={180} /></Group>
      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} mb="md">
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">Monitored sources</Text><Title order={2}>{sources.length}</Title><Text size="xs" c="dimmed">Sources with fetch telemetry</Text></Card>
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">Fetch success</Text><Title order={2}>{weightedSuccess.toFixed(1)}%</Title><Text size="xs" c="dimmed">Weighted across {fetches} attempts</Text></Card>
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">New article yield</Text><Title order={2}>{added}</Title><Text size="xs" c="dimmed">From {fetched} fetched items</Text></Card>
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">Duplicate rate</Text><Title order={2}>{fetched ? (duplicates / fetched * 100).toFixed(1) : "0.0"}%</Title><Text size="xs" c="dimmed">{duplicates} duplicate items</Text></Card>
      </SimpleGrid>
      <Card withBorder>
        <Group justify="space-between" mb="sm"><Title order={4}>Source health</Title><Text size="xs" c="dimmed">Click a source to inspect fetch history</Text></Group>
        <Table striped highlightOnHover>
          <Table.Thead><Table.Tr><Table.Th>Source</Table.Th><Table.Th>Health</Table.Th><Table.Th>Yield</Table.Th><Table.Th>Duplicates</Table.Th><Table.Th>Latency P95</Table.Th><Table.Th>Last success</Table.Th></Table.Tr></Table.Thead>
          <Table.Tbody>{sources.map((source) => (
            <Table.Tr key={source.source_id} onClick={() => setSelection({ title: source.source_name, kind: "sources", params: { source_id: source.source_id }, href: `/?source_id=${encodeURIComponent(source.source_name)}`, hrefLabel: "Open source articles" })} style={{ cursor: "pointer" }}>
              <Table.Td><Text fw={600}>{source.source_name}</Text><Text size="xs" c="dimmed">{source.category ?? "Uncategorized"}{source.country ? ` · ${source.country}` : ""}</Text></Table.Td>
              <Table.Td miw={130}><Group justify="space-between" gap="xs"><Badge color={source.success_rate >= 95 ? "teal" : source.success_rate >= 75 ? "yellow" : "red"} variant="light">{source.success_rate}%</Badge></Group><Progress value={source.success_rate} color={source.success_rate >= 95 ? "teal" : source.success_rate >= 75 ? "yellow" : "red"} size="xs" mt={6} /></Table.Td>
              <Table.Td>{source.new} / {source.fetched}</Table.Td>
              <Table.Td>{source.duplicate_rate}%</Table.Td>
              <Table.Td>{source.p95_latency_ms} ms</Table.Td>
              <Table.Td>{source.last_success_at ? new Date(source.last_success_at).toLocaleString() : "Never"}</Table.Td>
            </Table.Tr>
          ))}</Table.Tbody>
        </Table>
        {!sources.length ? <Text c="dimmed" py="xl" ta="center">No source telemetry in this period. Run the pipeline to establish a baseline.</Text> : null}
      </Card>
      <AnalyticsDrawer selection={selection} filters={filters} onClose={() => setSelection(null)} />
    </>
  );
}
