import { useEffect, useState } from "react";
import Chart from "react-apexcharts";
import { fetchStats } from "../lib/api";

export interface StatPoint { day: string; count: number }

export default function Analytics() {
  const [stats, setStats] = useState<{ articles_per_day: StatPoint[]; source_dist: { source: string; count: number }[] } | null>(null);

  useEffect(() => {
    fetchStats().then(setStats);
  }, []);

  const articlesSeries = stats?.articles_per_day?.map((p) => p.count) ?? [];
  const articlesCategories = stats?.articles_per_day?.map((p) => p.day) ?? [];

  const sourceSeries = stats?.source_dist?.map((s) => s.count) ?? [];
  const sourceLabels = stats?.source_dist?.map((s) => s.source) ?? [];

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Analytics</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 16 }}>
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
          <h3 style={{ marginTop: 0, fontSize: 14, color: "#475569" }}>Articles per day</h3>
          {stats && (
            <Chart
              type="area"
              height={260}
              series={[{ name: "Articles", data: articlesSeries }]}
              options={{ chart: { toolbar: { show: false } }, xaxis: { categories: articlesCategories }, dataLabels: { enabled: false }, stroke: { curve: "smooth" } }}
            />
          )}
        </div>
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
          <h3 style={{ marginTop: 0, fontSize: 14, color: "#475569" }}>Source distribution</h3>
          {stats && (
            <Chart
              type="pie"
              height={260}
              series={sourceSeries}
              options={{ labels: sourceLabels, legend: { position: "bottom" } }}
            />
          )}
        </div>
      </div>
      {!stats && <p style={{ color: "#64748b" }}>Loading...</p>}
    </div>
  );
}
