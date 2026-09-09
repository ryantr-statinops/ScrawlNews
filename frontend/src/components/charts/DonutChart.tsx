import Chart from "react-apexcharts";
import { useThemeStore } from "../../stores/themeStore";

interface DonutChartProps {
  labels: string[];
  series: number[];
}

export function DonutChart({ labels, series }: DonutChartProps) {
  const colorScheme = useThemeStore((state) => state.colorScheme);
  const isDark = colorScheme === "dark";
  const chartText = isDark ? "#C1C2C5" : "#495057";
  return (
    <Chart
      type="donut"
      height={260}
      series={series}
      options={{
        chart: { foreColor: chartText, background: "transparent", toolbar: { show: false } },
        labels,
        legend: { position: "bottom", labels: { colors: chartText } },
        dataLabels: { enabled: false },
        tooltip: { theme: isDark ? "dark" : "light" },
      }}
    />
  );
}
