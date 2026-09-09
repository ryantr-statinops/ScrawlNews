import Chart from "react-apexcharts";

interface BarChartProps {
  categories: string[];
  series: number[];
  secondarySeries?: number[];
}

export function BarChart({ categories, series, secondarySeries }: BarChartProps) {
  return (
    <Chart
      type="bar"
      height={280}
      series={secondarySeries ? [{ name: "articles", data: series }, { name: "summaries", data: secondarySeries }] : [{ name: "articles", data: series }]}
      options={{ xaxis: { categories }, dataLabels: { enabled: false } }}
    />
  );
}
