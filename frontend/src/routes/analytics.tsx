import { useQuery } from "@tanstack/react-query";
import { SimpleGrid, Card, Text } from "@mantine/core";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { BarChart } from "../components/charts/BarChart";
import { DonutChart } from "../components/charts/DonutChart";

async function fetchStats() {
  const res = await fetch("/api/stats?days=7");
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json();
}

export function AnalyticsPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["stats"], queryFn: fetchStats });
  const perDay: { day: string; count: number }[] = data?.articles_per_day ?? [];
  const sources: { source: string; count: number }[] = data?.source_dist ?? [];
  const cost = data?.cost_estimate ?? 0;

  return (
    <div>
      <PageHeader title="Analytics" description="Articles per day, source distribution, cost estimate" />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {data ? (
        <>
          <Card shadow="sm" mb="md" padding="md">
            <Text size="xs" c="dimmed">Cost estimate (7d)</Text>
            <Text size="xl" fw={600}>${Number(cost).toFixed(4)}</Text>
          </Card>
          <SimpleGrid cols={{ base: 1, md: 2 }}>
            <Card shadow="sm" padding="md">
              <Text size="sm" c="dimmed" mb="xs">Articles per day</Text>
              <BarChart categories={perDay.map((d) => d.day)} series={perDay.map((d) => d.count)} />
            </Card>
            <Card shadow="sm" padding="md">
              <Text size="sm" c="dimmed" mb="xs">Source distribution</Text>
              <DonutChart labels={sources.map((s) => s.source ?? "unknown")} series={sources.map((s) => s.count)} />
            </Card>
          </SimpleGrid>
        </>
      ) : null}
    </div>
  );
}
