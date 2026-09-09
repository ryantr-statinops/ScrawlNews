import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, Group, Select, SimpleGrid, Table, Text, Title } from "@mantine/core";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { BarChart } from "../components/charts/BarChart";
import { DonutChart } from "../components/charts/DonutChart";

async function fetchStats(days: number) {
  const res = await fetch(`/api/stats?days=${days}`);
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json();
}

export function AnalyticsPage() {
  const [days, setDays] = useState("7");
  const { data, isLoading, error } = useQuery({ queryKey: ["stats", days], queryFn: () => fetchStats(Number(days)) });
  const perDay: { day: string; count: number }[] = data?.articles_per_day ?? [];
  const summariesPerDay: { day: string; count: number }[] = data?.summaries_per_day ?? [];
  const sources: { source: string; count: number }[] = data?.source_dist ?? [];
  const categories: { category: string; count: number }[] = data?.category_dist ?? [];
  const totals = data?.totals ?? { articles: 0, summarized: 0, summaries: 0 };
  const summarizeRate = totals.articles ? Math.round((totals.summarized / totals.articles) * 100) : 0;

  return (
    <div>
      <Group justify="space-between" align="end" mb="md">
        <PageHeader title="Analytics" description="News intelligence and pipeline performance" />
        <Select label="Period" value={days} onChange={(value) => setDays(value ?? "7")} data={[{ value: "7", label: "Last 7 days" }, { value: "30", label: "Last 30 days" }, { value: "90", label: "Last 90 days" }]} w={160} />
      </Group>
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {data ? (
        <>
          <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} mb="md">
            <Card shadow="sm"><Text size="xs" c="dimmed">Articles collected</Text><Title order={2}>{totals.articles}</Title><Text size="xs" c="dimmed">Selected period</Text></Card>
            <Card shadow="sm"><Text size="xs" c="dimmed">Summaries generated</Text><Title order={2}>{totals.summaries}</Title><Text size="xs" c="dimmed">LLM + fallback summaries</Text></Card>
            <Card shadow="sm"><Text size="xs" c="dimmed">Summarization rate</Text><Title order={2} c={summarizeRate >= 80 ? "green" : "orange"}>{summarizeRate}%</Title><Text size="xs" c="dimmed">Articles marked summarized</Text></Card>
            <Card shadow="sm"><Text size="xs" c="dimmed">Estimated cost</Text><Title order={2}>${Number(data.cost_estimate ?? 0).toFixed(4)}</Title><Text size="xs" c="dimmed">Current estimate</Text></Card>
          </SimpleGrid>
          <Card shadow="sm" mb="md"><Text fw={600} mb="xs">Collection trend</Text><BarChart categories={perDay.map((item) => item.day)} series={perDay.map((item) => item.count)} secondarySeries={perDay.map((item) => summariesPerDay.find((summary) => summary.day === item.day)?.count ?? 0)} /></Card>
          <SimpleGrid cols={{ base: 1, md: 2 }} mb="md">
            <Card shadow="sm"><Text fw={600} mb="xs">Articles by category</Text><DonutChart labels={categories.map((item) => item.category)} series={categories.map((item) => item.count)} /></Card>
            <Card shadow="sm"><Text fw={600} mb="xs">Top sources</Text><Table striped><Table.Thead><Table.Tr><Table.Th>Source</Table.Th><Table.Th>Articles</Table.Th><Table.Th>Share</Table.Th></Table.Tr></Table.Thead><Table.Tbody>{sources.slice(0, 8).map((item) => <Table.Tr key={item.source}><Table.Td>{item.source}</Table.Td><Table.Td>{item.count}</Table.Td><Table.Td>{totals.articles ? `${Math.round((item.count / totals.articles) * 100)}%` : "0%"}</Table.Td></Table.Tr>)}</Table.Tbody></Table></Card>
          </SimpleGrid>
        </>
      ) : null}
    </div>
  );
}
