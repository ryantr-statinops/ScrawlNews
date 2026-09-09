import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Alert, Card, Group, SimpleGrid, Table, Text, Title } from "@mantine/core";
import { AlertTriangle, CircleGauge, Clock3, FileText, RadioTower, Sparkles } from "lucide-react";
import { BarChart } from "../../components/charts/BarChart";
import { LoadingState } from "../../components/ui/LoadingState";
import { ErrorState } from "../../components/ui/ErrorState";
import { analyticsApi } from "./api";
import { AnalyticsDrawer, type DrilldownSelection } from "./AnalyticsDrawer";
import { KpiCard } from "./KpiCard";
import type { AnalyticsFiltersState } from "./types";

const percent = (value: number) => `${value.toFixed(1)}%`;
const minutes = (value: number) => value >= 60 ? `${(value / 60).toFixed(1)}h` : `${Math.round(value)}m`;
const alertCopy: Record<string, string> = {
  pipeline: "pipeline runs failed",
  source: "source fetches need attention",
  summary_backlog: "articles are waiting for summaries",
  llm: "LLM requests failed",
};

export function OverviewTab({ filters }: { filters: AnalyticsFiltersState }) {
  const [selection, setSelection] = useState<DrilldownSelection | null>(null);
  const query = useQuery({ queryKey: ["analytics", "overview", filters], queryFn: () => analyticsApi.overview(filters) });
  if (query.isLoading) return <LoadingState />;
  if (query.error) return <ErrorState message={(query.error as Error).message} />;
  if (!query.data) return null;
  const { kpis, alerts, trend, categories, sources, period } = query.data;

  return (
    <>
      {alerts.length ? (
        <Alert icon={<AlertTriangle size={18} />} color="orange" title="Attention required" mb="md">
          {alerts.map((alert) => `${alert.count} ${alertCopy[alert.kind] ?? alert.kind}`).join(" · ")}
        </Alert>
      ) : (
        <Alert icon={<CircleGauge size={18} />} color="teal" title="All monitored systems are healthy" mb="md">
          No operational alerts in the selected window.
        </Alert>
      )}
      <SimpleGrid cols={{ base: 1, sm: 2, lg: 3, xl: 6 }} mb="md">
        <KpiCard label="New articles" metric={kpis.articles} onClick={() => setSelection({ title: "New articles", kind: "articles", href: "/", hrefLabel: "Open Feed" })} />
        <KpiCard label="Active sources" metric={kpis.active_sources} onClick={() => setSelection({ title: "Active sources", kind: "sources" })} />
        <KpiCard label="Median freshness" metric={kpis.freshness_minutes} format={minutes} inverse onClick={() => setSelection({ title: "Article freshness", kind: "articles", href: "/", hrefLabel: "Open Feed" })} />
        <KpiCard label="Summary coverage" metric={kpis.summary_coverage} format={percent} onClick={() => setSelection({ title: "Summary coverage", kind: "articles", href: "/summaries", hrefLabel: "Open Summaries" })} />
        <KpiCard label="Pipeline success" metric={kpis.pipeline_success_rate} format={percent} onClick={() => setSelection({ title: "Pipeline runs", kind: "runs", href: "/runs", hrefLabel: "Open Runs" })} />
        <KpiCard label="Total tokens" metric={kpis.total_tokens} onClick={() => setSelection({ title: "LLM calls", kind: "llm" })} />
      </SimpleGrid>
      <Card withBorder mb="md" onClick={() => setSelection({ title: "Content records", kind: "articles", href: "/", hrefLabel: "Open Feed" })} style={{ cursor: "pointer" }}>
        <Group justify="space-between" mb="sm">
          <div><Title order={4}>News velocity</Title><Text size="xs" c="dimmed">Articles and summaries · {period.timezone}</Text></div>
          <Group gap="xs"><FileText size={16} /><Sparkles size={16} /></Group>
        </Group>
        <BarChart categories={trend.map((item) => item.timestamp)} series={trend.map((item) => item.articles)} secondarySeries={trend.map((item) => item.summaries)} />
      </Card>
      <SimpleGrid cols={{ base: 1, lg: 2 }}>
        <Card withBorder>
          <Group gap="xs" mb="sm"><Title order={4}>Category snapshot</Title></Group>
          <Table highlightOnHover>
            <Table.Thead><Table.Tr><Table.Th>Category</Table.Th><Table.Th>Articles</Table.Th><Table.Th>Change</Table.Th></Table.Tr></Table.Thead>
            <Table.Tbody>{categories.map((row) => <Table.Tr key={String(row.category)} onClick={() => setSelection({ title: String(row.category), kind: "articles", params: { category: String(row.category) }, href: `/?category=${encodeURIComponent(String(row.category))}`, hrefLabel: "Open filtered Feed" })} style={{ cursor: "pointer" }}><Table.Td>{String(row.category)}</Table.Td><Table.Td>{row.current}</Table.Td><Table.Td>{row.delta > 0 ? "+" : ""}{row.delta}</Table.Td></Table.Tr>)}</Table.Tbody>
          </Table>
        </Card>
        <Card withBorder>
          <Group gap="xs" mb="sm"><RadioTower size={18} /><Title order={4}>Source snapshot</Title></Group>
          <Table highlightOnHover>
            <Table.Thead><Table.Tr><Table.Th>Source</Table.Th><Table.Th>Articles</Table.Th><Table.Th>Change</Table.Th></Table.Tr></Table.Thead>
            <Table.Tbody>{sources.map((row) => <Table.Tr key={String(row.source)} onClick={() => setSelection({ title: String(row.source), kind: "articles", params: { source_id: String(row.source) }, href: `/?source_id=${encodeURIComponent(String(row.source))}`, hrefLabel: "Open filtered Feed" })} style={{ cursor: "pointer" }}><Table.Td>{String(row.source)}</Table.Td><Table.Td>{row.current}</Table.Td><Table.Td>{row.delta > 0 ? "+" : ""}{row.delta}</Table.Td></Table.Tr>)}</Table.Tbody>
          </Table>
          {!sources.length ? <Group justify="center" py="xl"><Clock3 size={18} /><Text c="dimmed">No source activity yet.</Text></Group> : null}
        </Card>
      </SimpleGrid>
      <AnalyticsDrawer selection={selection} filters={filters} onClose={() => setSelection(null)} />
    </>
  );
}
