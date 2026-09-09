import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, SimpleGrid, Table, Text, Title } from "@mantine/core";
import { BarChart } from "../../components/charts/BarChart";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { analyticsApi } from "./api";
import { AnalyticsDrawer, type DrilldownSelection } from "./AnalyticsDrawer";
import { KpiCard } from "./KpiCard";
import type { AnalyticsFiltersState } from "./types";

const percent = (value: number) => `${value.toFixed(1)}%`;
const milliseconds = (value: number) => value >= 1000 ? `${(value / 1000).toFixed(1)}s` : `${Math.round(value)}ms`;

interface BreakdownProps {
  title: string;
  dimension: "provider" | "model" | "operation";
  rows: Array<Record<string, string | number>>;
  onSelect: (selection: DrilldownSelection) => void;
}

function Breakdown({ title, dimension, rows, onSelect }: BreakdownProps) {
  return (
    <Card withBorder>
      <Title order={4} mb="sm">{title}</Title>
      <Table striped highlightOnHover>
        <Table.Thead><Table.Tr><Table.Th>{dimension}</Table.Th><Table.Th>Requests</Table.Th><Table.Th>Tokens</Table.Th><Table.Th>Failures</Table.Th></Table.Tr></Table.Thead>
        <Table.Tbody>{rows.map((row) => {
          const value = String(row[dimension]);
          return <Table.Tr key={value} onClick={() => onSelect({ title: `${title}: ${value}`, kind: "llm", params: { [dimension]: value } })} style={{ cursor: "pointer" }}><Table.Td>{value}</Table.Td><Table.Td>{row.requests}</Table.Td><Table.Td>{Number(row.total_tokens).toLocaleString()}</Table.Td><Table.Td>{row.failures}</Table.Td></Table.Tr>;
        })}</Table.Tbody>
      </Table>
      {!rows.length ? <Text c="dimmed" py="lg">No AI calls recorded.</Text> : null}
    </Card>
  );
}

export function AiUsageTab({ filters }: { filters: AnalyticsFiltersState }) {
  const [selection, setSelection] = useState<DrilldownSelection | null>(null);
  const query = useQuery({ queryKey: ["analytics", "ai-usage", filters], queryFn: () => analyticsApi.aiUsage(filters) });
  if (query.isLoading) return <LoadingState />;
  if (query.error) return <ErrorState message={(query.error as Error).message} />;
  if (!query.data) return null;
  const { kpis, trend, providers, models, operations } = query.data;
  const inspectCalls = () => setSelection({ title: "LLM calls", kind: "llm" });

  return (
    <>
      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} mb="md">
        <KpiCard label="Total tokens" metric={kpis.total_tokens} onClick={inspectCalls} />
        <KpiCard label="Input tokens" metric={kpis.input_tokens} onClick={inspectCalls} />
        <KpiCard label="Output tokens" metric={kpis.output_tokens} onClick={inspectCalls} />
        <KpiCard label="Requests" metric={kpis.requests} onClick={inspectCalls} />
        <KpiCard label="Failure rate" metric={kpis.failure_rate} format={percent} inverse onClick={inspectCalls} />
        <KpiCard label="Median latency" metric={kpis.median_latency_ms} format={milliseconds} inverse onClick={inspectCalls} />
        <KpiCard label="P95 latency" metric={kpis.p95_latency_ms} format={milliseconds} inverse onClick={inspectCalls} />
      </SimpleGrid>
      <Card withBorder mb="md" onClick={inspectCalls} style={{ cursor: "pointer" }}>
        <Title order={4} mb="sm">Token usage trend</Title>
        <BarChart categories={trend.map((row) => row.timestamp)} series={trend.map((row) => row.input_tokens)} secondarySeries={trend.map((row) => row.output_tokens)} seriesName="input tokens" secondarySeriesName="output tokens" />
      </Card>
      <SimpleGrid cols={{ base: 1, xl: 3 }}>
        <Breakdown title="Providers" dimension="provider" rows={providers} onSelect={setSelection} />
        <Breakdown title="Models" dimension="model" rows={models} onSelect={setSelection} />
        <Breakdown title="Operations" dimension="operation" rows={operations} onSelect={setSelection} />
      </SimpleGrid>
      <AnalyticsDrawer selection={selection} filters={filters} onClose={() => setSelection(null)} />
    </>
  );
}
