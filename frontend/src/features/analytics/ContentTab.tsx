import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, Group, SimpleGrid, Table, Text, Title } from "@mantine/core";
import { BarChart } from "../../components/charts/BarChart";
import { DonutChart } from "../../components/charts/DonutChart";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { analyticsApi } from "./api";
import { AnalyticsDrawer, type DrilldownSelection } from "./AnalyticsDrawer";
import type { AnalyticsFiltersState } from "./types";

const freshnessLabels: Record<string, string> = {
  under_1h: "Under 1 hour",
  "1h_6h": "1–6 hours",
  "6h_24h": "6–24 hours",
  over_24h: "Over 24 hours",
};

export function ContentTab({ filters }: { filters: AnalyticsFiltersState }) {
  const [selection, setSelection] = useState<DrilldownSelection | null>(null);
  const query = useQuery({ queryKey: ["analytics", "content", filters], queryFn: () => analyticsApi.content(filters) });
  if (query.isLoading) return <LoadingState />;
  if (query.error) return <ErrorState message={(query.error as Error).message} />;
  if (!query.data) return null;
  const { velocity, categories, sources, diversity, freshness, period } = query.data;
  const totalArticles = velocity.reduce((sum, row) => sum + row.articles, 0);
  const freshArticles = (freshness.under_1h ?? 0) + (freshness["1h_6h"] ?? 0);
  const freshRate = totalArticles ? Math.round(freshArticles / totalArticles * 100) : 0;

  return (
    <>
      <SimpleGrid cols={{ base: 1, sm: 3 }} mb="md">
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">Articles</Text><Title order={2}>{totalArticles}</Title><Text size="xs" c="dimmed">Collected in {period.window}</Text></Card>
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">Source diversity</Text><Title order={2}>{diversity}</Title><Text size="xs" c="dimmed">Distinct publishers represented</Text></Card>
        <Card withBorder><Text size="xs" tt="uppercase" fw={700} c="dimmed">Fresh within 6h</Text><Title order={2}>{freshRate}%</Title><Text size="xs" c="dimmed">Based on published time when available</Text></Card>
      </SimpleGrid>
      <Card withBorder mb="md" onClick={() => setSelection({ title: "Content timeline", kind: "articles", href: "/", hrefLabel: "Open Feed" })} style={{ cursor: "pointer" }}>
        <Group justify="space-between" mb="sm"><div><Title order={4}>News velocity</Title><Text size="xs" c="dimmed">Volume in {period.timezone}</Text></div><Text size="xs" c="dimmed">Click to inspect articles</Text></Group>
        <BarChart categories={velocity.map((row) => row.timestamp)} series={velocity.map((row) => row.articles)} secondarySeries={velocity.map((row) => row.summaries)} />
      </Card>
      <SimpleGrid cols={{ base: 1, lg: 2 }} mb="md">
        <Card withBorder>
          <Title order={4} mb="sm">Category mix</Title>
          <DonutChart labels={categories.map((row) => String(row.category))} series={categories.map((row) => row.current)} />
        </Card>
        <Card withBorder>
          <Title order={4} mb="sm">Freshness distribution</Title>
          <DonutChart labels={Object.keys(freshness).map((key) => freshnessLabels[key] ?? key)} series={Object.values(freshness)} />
        </Card>
      </SimpleGrid>
      <SimpleGrid cols={{ base: 1, xl: 2 }}>
        <Card withBorder>
          <Title order={4} mb="sm">Category movement</Title>
          <Table striped highlightOnHover>
            <Table.Thead><Table.Tr><Table.Th>Category</Table.Th><Table.Th>Current</Table.Th><Table.Th>Previous</Table.Th><Table.Th>Delta</Table.Th></Table.Tr></Table.Thead>
            <Table.Tbody>{categories.map((row) => {
              const category = String(row.category);
              return <Table.Tr key={category} onClick={() => setSelection({ title: `${category} articles`, kind: "articles", params: { category }, href: `/?category=${encodeURIComponent(category)}`, hrefLabel: "Open filtered Feed" })} style={{ cursor: "pointer" }}><Table.Td>{category}</Table.Td><Table.Td>{row.current}</Table.Td><Table.Td>{row.previous}</Table.Td><Table.Td c={row.delta >= 0 ? "teal" : "red"}>{row.delta > 0 ? "+" : ""}{row.delta}</Table.Td></Table.Tr>;
            })}</Table.Tbody>
          </Table>
        </Card>
        <Card withBorder>
          <Title order={4} mb="sm">Source coverage</Title>
          <Table striped highlightOnHover>
            <Table.Thead><Table.Tr><Table.Th>Source</Table.Th><Table.Th>Current</Table.Th><Table.Th>Previous</Table.Th><Table.Th>Share</Table.Th></Table.Tr></Table.Thead>
            <Table.Tbody>{sources.slice(0, 12).map((row) => {
              const source = String(row.source);
              return <Table.Tr key={source} onClick={() => setSelection({ title: `${source} articles`, kind: "articles", params: { source_id: source }, href: `/?source_id=${encodeURIComponent(source)}`, hrefLabel: "Open filtered Feed" })} style={{ cursor: "pointer" }}><Table.Td>{source}</Table.Td><Table.Td>{row.current}</Table.Td><Table.Td>{row.previous}</Table.Td><Table.Td>{totalArticles ? Math.round(row.current / totalArticles * 100) : 0}%</Table.Td></Table.Tr>;
            })}</Table.Tbody>
          </Table>
        </Card>
      </SimpleGrid>
      <AnalyticsDrawer selection={selection} filters={filters} onClose={() => setSelection(null)} />
    </>
  );
}
