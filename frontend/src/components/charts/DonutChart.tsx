import Chart from "react-apexcharts";

interface DonutChartProps {
  labels: string[];
  series: number[];
}

export function DonutChart({ labels, series }: DonutChartProps) {
  return (
    <Chart
      type="donut"
      height={260}
      series={series}
      options={{ labels, legend: { position: "bottom" }, dataLabels: { enabled: false } }}
    />
  );
}
