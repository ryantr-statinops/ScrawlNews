import Chart from "react-apexcharts";

interface BarChartProps {
  categories: string[];
  series: number[];
}

export function BarChart({ categories, series }: BarChartProps) {
  return (
    <Chart
      type="bar"
      height={280}
      series={[{ name: "articles", data: series }]}
      options={{ xaxis: { categories }, dataLabels: { enabled: false } }}
    />
  );
}
