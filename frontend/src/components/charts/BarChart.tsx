import Chart from "react-apexcharts";
import { useThemeStore } from "../../stores/themeStore";

interface BarChartProps {
  categories: string[];
  series: number[];
  secondarySeries?: number[];
  seriesName?: string;
  secondarySeriesName?: string;
}

export function BarChart({ categories, series, secondarySeries, seriesName = "articles", secondarySeriesName = "summaries" }: BarChartProps) {
  const colorScheme = useThemeStore((state) => state.colorScheme);
  const isDark = colorScheme === "dark";
  const chartText = isDark ? "#C1C2C5" : "#495057";
  const gridColor = isDark ? "#373A40" : "#DEE2E6";
  return (
    <Chart
      type="bar"
      height={280}
      series={secondarySeries ? [{ name: seriesName, data: series }, { name: secondarySeriesName, data: secondarySeries }] : [{ name: seriesName, data: series }]}
      options={{
        chart: { foreColor: chartText, background: "transparent", toolbar: { show: false } },
        xaxis: { categories, labels: { style: { colors: chartText } } },
        yaxis: { labels: { style: { colors: chartText } } },
        grid: { borderColor: gridColor },
        dataLabels: { enabled: false },
        tooltip: { theme: isDark ? "dark" : "light" },
      }}
    />
  );
}
