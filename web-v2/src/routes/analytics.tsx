import { useQuery } from "@tanstack/react-query";
import { Card } from "@mantine/core";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { BarChart } from "../components/charts/BarChart";

async function fetchStats() {
  const res = await fetch("/api/stats?days=7");
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json();
}

export function AnalyticsPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["stats"], queryFn: fetchStats });
  const perDay: { day: string; count: number }[] = data?.articles_per_day ?? [];

  return (
    <div>
      <PageHeader title="Analytics" description="Articles per day, source distribution, cost" />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {data ? (
        <Card shadow="sm">
          <BarChart
            categories={perDay.map((d) => d.day)}
            series={perDay.map((d) => d.count)}
          />
        </Card>
      ) : null}
    </div>
  );
}
