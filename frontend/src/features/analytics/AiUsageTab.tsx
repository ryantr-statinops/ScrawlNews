import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Alert, Card, SimpleGrid, Table, Text, Title } from "@mantine/core";
import { BarChart } from "../../components/charts/BarChart";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { analyticsApi } from "./api";
import { AnalyticsDrawer, type DrilldownSelection } from "./AnalyticsDrawer";
import { KpiCard } from "./KpiCard";
import type { AnalyticsFiltersState } from "./types";

const percent = (value: number) => `${value.toFixed(1)}%`;
const milliseconds = (value: number) => value >= 1000 ? `${(value / 1000).toFixed(1)}s` : `${Math.round(value)}ms`;
const dollars = (value: number) => "$" + value.toFixed(6);

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
      <Table.ScrollContainer minWidth={440}><Table striped highlightOnHover>
        <Table.Thead><Table.Tr><Table.Th>{dimension}</Table.Th><Table.Th>Requests</Table.Th><Table.Th>Tokens</Table.Th><Table.Th>Failures</Table.Th></Table.Tr></Table.Thead>
        <Table.Tbody>{rows.map((row) => {
          const value = String(row[dimension]);
          return <Table.Tr key={value} onClick={() => onSelect({ title: `${title}: ${value}`, kind: "llm", params: { [dimension]: value } })} style={{ cursor: "pointer" }}><Table.Td>{value}</Table.Td><Table.Td>{row.requests}</Table.Td><Table.Td>{Number(row.total_tokens).toLocaleString()}</Table.Td><Table.Td>{row.failures}</Table.Td></Table.Tr>;
        })}</Table.Tbody>
      </Table></Table.ScrollContainer>
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
  const { kpis, cost, trend, providers, models, operations } = query.data;
  const inspectCalls = () => setSelection({ title: "LLM calls", kind: "llm" });

  return (
    <>
      {cost.alert && <Alert color="yellow" title="Monthly AI budget warning" mb="md">
        Projected monthly cost {dollars(cost.monthly_estimate_usd)} meets or exceeds the budget of {dollars(cost.monthly_budget_usd)}
        {cost.budget_usage_percent !== null ? " (" + cost.budget_usage_percent.toFixed(1) + "% used)" : ""}. This is a warning only; AI calls continue.
      </Alert>}
      {!cost.pricing_complete && <Alert color="yellow" title="Pricing incomplete" mb="md">
        Cost excludes {cost.unpriced_tokens.toLocaleString()} unpriced tokens. Add prices for: {cost.unpriced_models.join(", ")}.
      </Alert>}
      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} mb="md">
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">Estimated cost</Text><Title order={2}>{dollars(cost.window_estimated_usd)}</Title><Text size="xs" c="dimmed">Selected window</Text></Card>
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">Monthly estimate</Text><Title order={2}>{dollars(cost.monthly_estimate_usd)}</Title><Text size="xs" c="dimmed">Month to date: {dollars(cost.month_to_date_usd)}</Text></Card>
        <KpiCard label="Total tokens" metric={kpis.total_tokens} onClick={inspectCalls} />
        <KpiCard label="Input tokens" metric={kpis.input_tokens} onClick={inspectCalls} />
        <KpiCard label="Output tokens" metric={kpis.output_tokens} onClick={inspectCalls} />
        <KpiCard label="Requests" metric={kpis.requests} onClick={inspectCalls} />
        <KpiCard label="Failure rate" metric={kpis.failure_rate} format={percent} inverse onClick={inspectCalls} />
        <KpiCard label="Median latency" metric={kpis.median_latency_ms} format={milliseconds} inverse onClick={inspectCalls} />
        <KpiCard label="P95 latency" metric={kpis.p95_latency_ms} format={milliseconds} inverse onClick={inspectCalls} />
      </SimpleGrid>
      <Card withBorder mb="md" role="button" tabIndex={0} aria-label="Inspect LLM calls" onKeyDown={(event) => { if (event.key === "Enter") inspectCalls(); }} onClick={inspectCalls} style={{ cursor: "pointer" }}>
        <Title order={4} mb="sm">Token usage trend</Title>
        {trend.length ? <BarChart categories={trend.map((row) => row.timestamp)} series={trend.map((row) => row.input_tokens)} secondarySeries={trend.map((row) => row.output_tokens)} seriesName="input tokens" secondarySeriesName="output tokens" /> : <Text c="dimmed" py="xl" ta="center">No LLM usage telemetry yet. Token usage appears after the next summarized run.</Text>}
      </Card>
      <SimpleGrid cols={{ base: 1, xl: 3 }}>
        <Breakdown title="Providers" dimension="provider" rows={providers} onSelect={setSelection} />
        <Breakdown title="Models" dimension="model" rows={models} onSelect={setSelection} />
        <Breakdown title="Model activities" dimension="operation" rows={operations} onSelect={setSelection} />
      </SimpleGrid>
      <AnalyticsDrawer selection={selection} filters={filters} onClose={() => setSelection(null)} />
    </>
  );
}
