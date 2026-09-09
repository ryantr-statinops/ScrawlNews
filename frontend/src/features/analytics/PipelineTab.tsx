import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge, Card, SimpleGrid, Table, Text, Title } from "@mantine/core";
import { BarChart } from "../../components/charts/BarChart";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { analyticsApi } from "./api";
import { AnalyticsDrawer, type DrilldownSelection } from "./AnalyticsDrawer";
import { KpiCard } from "./KpiCard";
import type { AnalyticsFiltersState } from "./types";

const percent = (value: number) => `${value.toFixed(1)}%`;
const seconds = (value: number) => `${value.toFixed(1)}s`;

export function PipelineTab({ filters }: { filters: AnalyticsFiltersState }) {
  const [selection, setSelection] = useState<DrilldownSelection | null>(null);
  const query = useQuery({ queryKey: ["analytics", "pipeline", filters.window], queryFn: () => analyticsApi.pipeline(filters) });
  if (query.isLoading) return <LoadingState />;
  if (query.error) return <ErrorState message={(query.error as Error).message} />;
  if (!query.data) return null;
  const { kpis, stages, errors, runs } = query.data;

  return (
    <>
      <SimpleGrid cols={{ base: 1, sm: 2, lg: 5 }} mb="md">
        <KpiCard label="Runs" metric={kpis.runs} onClick={() => setSelection({ title: "Pipeline runs", kind: "runs", href: "/runs", hrefLabel: "Open Runs" })} />
        <KpiCard label="Success rate" metric={kpis.success_rate} format={percent} onClick={() => setSelection({ title: "Pipeline runs", kind: "runs", href: "/runs", hrefLabel: "Open Runs" })} />
        <KpiCard label="Throughput" metric={kpis.throughput} onClick={() => setSelection({ title: "Pipeline runs", kind: "runs" })} />
        <KpiCard label="Median duration" metric={kpis.median_duration_seconds} format={seconds} inverse onClick={() => setSelection({ title: "Stage timings", kind: "stages" })} />
        <KpiCard label="P95 duration" metric={kpis.p95_duration_seconds} format={seconds} inverse onClick={() => setSelection({ title: "Stage timings", kind: "stages" })} />
      </SimpleGrid>
      <Card withBorder mb="md">
        <Title order={4} mb="sm">Stage duration</Title>
        <BarChart categories={stages.map((stage) => stage.stage)} series={stages.map((stage) => stage.median_seconds)} secondarySeries={stages.map((stage) => stage.p95_seconds)} seriesName="median seconds" secondarySeriesName="p95 seconds" />
      </Card>
      <SimpleGrid cols={{ base: 1, xl: 2 }}>
        <Card withBorder>
          <Title order={4} mb="sm">Recent runs</Title>
          <Table striped highlightOnHover>
            <Table.Thead><Table.Tr><Table.Th>Run</Table.Th><Table.Th>Status</Table.Th><Table.Th>Articles</Table.Th><Table.Th>Started</Table.Th></Table.Tr></Table.Thead>
            <Table.Tbody>{runs.map((run) => {
              const id = String(run.id);
              const status = String(run.status);
              return <Table.Tr key={id} onClick={() => setSelection({ title: `Run ${id}`, kind: "stages", params: { run_id: id }, href: "/runs", hrefLabel: "Open Runs" })} style={{ cursor: "pointer" }}><Table.Td>{id.slice(0, 8)}</Table.Td><Table.Td><Badge color={status === "success" ? "teal" : status === "failed" ? "red" : "blue"} variant="light">{status}</Badge></Table.Td><Table.Td>{run.articles_fetched ?? 0}</Table.Td><Table.Td>{run.started_at ? new Date(String(run.started_at)).toLocaleString() : "—"}</Table.Td></Table.Tr>;
            })}</Table.Tbody>
          </Table>
          {!runs.length ? <Text c="dimmed" py="lg">No pipeline runs in this window.</Text> : null}
        </Card>
        <Card withBorder>
          <Title order={4} mb="sm">Error breakdown</Title>
          <Table striped>
            <Table.Thead><Table.Tr><Table.Th>Stage</Table.Th><Table.Th>Error class</Table.Th><Table.Th>Count</Table.Th></Table.Tr></Table.Thead>
            <Table.Tbody>{errors.map((error) => <Table.Tr key={`${error.stage}-${error.error_class}`}><Table.Td>{error.stage}</Table.Td><Table.Td>{error.error_class}</Table.Td><Table.Td>{error.count}</Table.Td></Table.Tr>)}</Table.Tbody>
          </Table>
          {!errors.length ? <Text c="teal" py="lg">No stage errors recorded.</Text> : null}
        </Card>
      </SimpleGrid>
      <AnalyticsDrawer selection={selection} filters={filters} onClose={() => setSelection(null)} />
    </>
  );
}
