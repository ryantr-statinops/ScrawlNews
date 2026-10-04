import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { BarChart } from "../components/charts/BarChart";
import { DonutChart } from "../components/charts/DonutChart";
import { useThemeStore } from "../stores/themeStore";
import { theme } from "../theme";

interface CapturedProps {
  type?: string;
  height?: number;
  series?: unknown;
  options?: {
    chart?: { foreColor?: string; toolbar?: { show?: boolean }; animations?: { enabled?: boolean } };
    xaxis?: { categories?: string[]; labels?: { style?: { colors?: string } } };
    labels?: string[];
    legend?: { position?: string; labels?: { colors?: string } };
    dataLabels?: { enabled?: boolean };
    tooltip?: { theme?: string };
    grid?: { borderColor?: string };
  };
}

const charts: CapturedProps[] = [];

vi.mock("react-apexcharts", () => ({
  default: (props: CapturedProps) => {
    charts.push(props);
    return <div data-testid="apex-chart" />;
  },
}));

afterEach(() => {
  charts.length = 0;
  cleanup();
  useThemeStore.getState().set("dark");
});

function renderChart(ui: React.ReactElement) {
  return render(<MantineProvider theme={theme}>{ui}</MantineProvider>);
}

function lastChart(): CapturedProps {
  expect(charts.length).toBeGreaterThan(0);
  return charts[charts.length - 1];
}

describe("charts", () => {
  it("renders a single-series bar chart with the requested categories and light palette", () => {
    useThemeStore.getState().set("light");
    renderChart(<BarChart categories={["fetch", "summarize"]} series={[3, 5]} />);
    expect(screen.getByTestId("apex-chart")).toBeInTheDocument();
    const chart = lastChart();
    expect(chart.type).toBe("bar");
    expect(chart.height).toBe(280);
    expect(chart.series).toEqual([{ name: "articles", data: [3, 5] }]);
    expect(chart.options?.xaxis?.categories).toEqual(["fetch", "summarize"]);
    expect(chart.options?.chart?.foreColor).toBe("#495057");
    expect(chart.options?.grid?.borderColor).toBe("#DEE2E6");
    expect(chart.options?.tooltip?.theme).toBe("light");
    expect(chart.options?.dataLabels?.enabled).toBe(false);
    expect(chart.options?.chart?.toolbar?.show).toBe(false);
    expect(chart.options?.chart?.animations?.enabled).toBe(false);
  });

  it("adds the secondary bar series with custom names and uses the dark palette", () => {
    renderChart(
      <BarChart
        categories={["fetch", "summarize"]}
        series={[1.5, 2.5]}
        secondarySeries={[3, 4]}
        seriesName="median seconds"
        secondarySeriesName="p95 seconds"
      />,
    );
    const chart = lastChart();
    expect(chart.series).toEqual([
      { name: "median seconds", data: [1.5, 2.5] },
      { name: "p95 seconds", data: [3, 4] },
    ]);
    expect(chart.options?.chart?.foreColor).toBe("#C1C2C5");
    expect(chart.options?.grid?.borderColor).toBe("#373A40");
    expect(chart.options?.tooltip?.theme).toBe("dark");
    expect(chart.options?.xaxis?.labels?.style?.colors).toBe("#C1C2C5");
  });

  it("renders a donut chart with legend labels that follow the color scheme", () => {
    useThemeStore.getState().set("light");
    renderChart(<DonutChart labels={["success", "failed"]} series={[8, 2]} />);
    let chart = lastChart();
    expect(chart.type).toBe("donut");
    expect(chart.height).toBe(260);
    expect(chart.series).toEqual([8, 2]);
    expect(chart.options?.labels).toEqual(["success", "failed"]);
    expect(chart.options?.legend).toEqual({ position: "bottom", labels: { colors: "#495057" } });
    expect(chart.options?.tooltip?.theme).toBe("light");

    cleanup();
    useThemeStore.getState().set("dark");
    renderChart(<DonutChart labels={["success"]} series={[1]} />);
    chart = lastChart();
    expect(chart.options?.legend).toEqual({ position: "bottom", labels: { colors: "#C1C2C5" } });
    expect(chart.options?.tooltip?.theme).toBe("dark");
    expect(chart.options?.dataLabels?.enabled).toBe(false);
  });
});
