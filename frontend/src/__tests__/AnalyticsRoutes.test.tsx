import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import { renderWithProviders } from "../test-utils";
import { AiUsageTab } from "../features/analytics/AiUsageTab";
import { ContentTab } from "../features/analytics/ContentTab";
import { OverviewTab } from "../features/analytics/OverviewTab";
import { SourcesTab } from "../features/analytics/SourcesTab";
import type {
  AiUsageResponse,
  AnalyticsFiltersState,
  AnalyticsPeriod,
  ContentResponse,
  OverviewResponse,
  SourceAnalyticsResponse,
} from "../features/analytics/types";

vi.mock("../components/charts/BarChart", () => ({ BarChart: () => null }));
vi.mock("../components/charts/DonutChart", () => ({ DonutChart: () => null }));

// The real Mantine Select is prohibitively slow in jsdom (it hangs the Sources
// tab country filter), so tests inject a native select that keeps the same
// value/onChange contract. No production code is modified.
vi.mock("@mantine/core", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@mantine/core")>();
  return {
    ...actual,
    Select: (props: {
      label?: unknown;
      value?: string | null;
      data?: Array<string | { value: string; label: string }>;
      placeholder?: string;
      clearable?: boolean;
      onChange?: (value: string | null) => void;
    }) => {
      const data = Array.isArray(props.data) ? props.data : [];
      const options = data.map((item) => (typeof item === "string" ? { value: item, label: item } : item));
      return (
        <select
          aria-label={String(props.label ?? "filter")}
          value={props.value ?? ""}
          onChange={(event) => props.onChange?.(event.target.value === "" ? null : event.target.value)}
        >
          <option value="">{props.placeholder ?? String(props.label ?? "")}</option>
          {options.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      );
    },
  };
});

const filters: AnalyticsFiltersState = {
  window: "7d",
  category: "World News",
  sourceId: "Daily/VN",
  provider: "azure/openai",
  model: "gpt+4",
};
const period: AnalyticsPeriod = { window: "7d", timezone: "UTC", current: { from: "", to: "" }, previous: { from: "", to: "" } };
const metric = { current: 4, previous: 2, delta: 2, delta_percent: 100 };
const overview: OverviewResponse = {
  period,
  kpis: {
    articles: metric,
    active_sources: metric,
    freshness_minutes: metric,
    summary_coverage: metric,
    pipeline_success_rate: metric,
    total_tokens: metric,
  },
  alerts: [],
  trend: [],
  categories: [],
  sources: [],
};
const content: ContentResponse = { period, velocity: [], categories: [], sources: [], diversity: 0, freshness: {} };
const sources: SourceAnalyticsResponse = { period, sources: [] };
const usage: AiUsageResponse = {
  period,
  kpis: {
    total_tokens: metric,
    input_tokens: metric,
    output_tokens: metric,
    requests: metric,
    failure_rate: metric,
    median_latency_ms: metric,
    p95_latency_ms: metric,
  },
  trend: [],
  providers: [],
  models: [],
  operations: [],
  cost: {
    window_estimated_usd: 0,
    month_to_date_usd: 0,
    monthly_estimate_usd: 0,
    monthly_budget_usd: 0,
    budget_usage_percent: null,
    alert: false,
    pricing_complete: true,
    unpriced_tokens: 0,
    unpriced_models: [],
  },
};

const json = (body: unknown, status = 200) => ({ ok: status < 400, status, text: async () => JSON.stringify(body) });
const requests: URL[] = [];
let failing: string | null = null;
function stubApi() {
  requests.length = 0;
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    const parsed = new URL(url, "http://localhost");
    requests.push(parsed);
    if (failing && parsed.pathname === failing) return json({ error: "Telemetry temporarily unavailable" }, 503);
    if (parsed.pathname.endsWith("/overview")) return json(overview);
    if (parsed.pathname.endsWith("/content")) return json(content);
    if (parsed.pathname.endsWith("/sources")) return json(sources);
    if (parsed.pathname.endsWith("/ai-usage")) return json(usage);
    return json({ error: "unknown route" }, 404);
  }));
}
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  failing = null;
  overview.alerts = [];
  content.velocity = [];
  content.categories = [];
  content.sources = [];
  content.diversity = 0;
  content.freshness = {};
  sources.sources = [];
});

describe("analytics tab data", () => {
  it("serializes tab filters into the analytics request query with form encoding", async () => {
    stubApi();
    renderWithProviders(<OverviewTab filters={filters} />);
    expect(await screen.findByText("All monitored systems are healthy")).toBeInTheDocument();
    expect(requests).toHaveLength(1);
    expect(requests[0].pathname).toBe("/api/analytics/overview");
    expect(requests[0].search).toBe("?window=7d&category=World+News&source_id=Daily%2FVN&provider=azure%2Fopenai&model=gpt%2B4");
    expect(requests[0].searchParams.get("category")).toBe("World News");
    expect(requests[0].searchParams.get("source_id")).toBe("Daily/VN");
    expect(requests[0].searchParams.get("model")).toBe("gpt+4");
  });

  it("renders a healthy overview with KPI values from telemetry", async () => {
    stubApi();
    renderWithProviders(<OverviewTab filters={filters} />);
    expect(await screen.findByText("All monitored systems are healthy")).toBeInTheDocument();
    const articles = within(screen.getByRole("button", { name: "Inspect New articles" }));
    expect(articles.getByText("4")).toBeInTheDocument();
    expect(articles.getByText("100%")).toBeInTheDocument();
    expect(articles.getByText("Previous: 2")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Inspect Summary coverage" })).toHaveTextContent("4.0%");
  });

  it("renders operational alerts when telemetry reports them", async () => {
    stubApi();
    overview.alerts = [{ severity: "warning", kind: "pipeline", count: 3 }];
    renderWithProviders(<OverviewTab filters={filters} />);
    expect(await screen.findByText("Attention required")).toBeInTheDocument();
    expect(screen.getByText("3 pipeline runs failed")).toBeInTheDocument();
    expect(screen.queryByText("All monitored systems are healthy")).not.toBeInTheDocument();
  });

  it("renders populated content insights from telemetry", async () => {
    stubApi();
    content.velocity = [{ timestamp: "09:00", articles: 5, summaries: 2 }];
    content.categories = [{ category: "World", current: 3, previous: 1, delta: 2, delta_percent: 100 }];
    content.sources = [{ source: "Daily/VN", current: 3, previous: 1, delta: 2, delta_percent: 100 }];
    content.diversity = 1;
    content.freshness = { under_1h: 3, "1h_6h": 2 };
    renderWithProviders(<ContentTab filters={filters} />);
    expect(await screen.findByRole("heading", { name: "Category mix" })).toBeInTheDocument();
    expect(screen.getByText("5", { selector: "h2" })).toBeInTheDocument();
    expect(screen.getByText("1", { selector: "h2" })).toBeInTheDocument();
    expect(screen.getByText("100%", { selector: "h2" })).toBeInTheDocument();
    const categoryRow = await screen.findByRole("row", { name: /World/ });
    expect(within(categoryRow).getByText("+2")).toBeInTheDocument();
    const sourceRow = screen.getByRole("row", { name: /Daily\/VN/ });
    expect(within(sourceRow).getByText("60%")).toBeInTheDocument();
  });

  it("renders empty content insights when the period has no telemetry", async () => {
    stubApi();
    renderWithProviders(<ContentTab filters={filters} />);
    expect(await screen.findByRole("heading", { name: "Category mix" })).toBeInTheDocument();
    expect(screen.getAllByText("0", { selector: "h2" })).toHaveLength(2);
    expect(screen.getByText("0%", { selector: "h2" })).toBeInTheDocument();
  });

  it("renders source health bands and serializes filters into the sources request", async () => {
    stubApi();
    const row = (id: string, rate: number) => ({
      source_id: id,
      source_name: id,
      category: "world",
      country: "VN",
      fetches: 10,
      success_rate: rate,
      fetched: 20,
      new: 5,
      duplicates: 2,
      duplicate_rate: 10,
      median_latency_ms: 100,
      p95_latency_ms: 300,
      last_success_at: null,
      last_error: null,
    });
    sources.sources = [row("Healthy Feed", 95), row("Warning Feed", 75), row("Fallback Feed", 74.9)];
    renderWithProviders(<SourcesTab filters={filters} />);
    const bands: Array<[string, string, string]> = [
      ["Healthy Feed", "95", "teal"],
      ["Warning Feed", "75", "yellow"],
      ["Fallback Feed", "74.9", "red"],
    ];
    for (const [name, rate, color] of bands) {
      const rowElement = await screen.findByRole("row", { name: new RegExp(name) });
      const badge = within(rowElement).getByText(`${rate}%`);
      expect(badge.parentElement?.getAttribute("style")).toMatch(new RegExp(`mantine-color-${color}`));
      expect(within(rowElement).getByRole("progressbar")).toHaveAttribute("aria-valuenow", rate);
    }
    expect(requests[0].pathname).toBe("/api/analytics/sources");
    expect(requests[0].search).toContain("source_id=Daily%2FVN");
    expect(requests[0].searchParams.get("window")).toBe("7d");
  });

  it("renders the empty source state when no source has telemetry", async () => {
    stubApi();
    renderWithProviders(<SourcesTab filters={filters} />);
    expect(await screen.findByText(/No source telemetry in this period/)).toBeInTheDocument();
  });

  it("renders empty AI usage from telemetry", async () => {
    stubApi();
    renderWithProviders(<AiUsageTab filters={filters} />);
    expect(await screen.findByText(/No LLM usage telemetry yet/)).toBeInTheDocument();
    expect(screen.getAllByText("No AI calls recorded.")).toHaveLength(3);
  });

  it.each([
    [OverviewTab, "overview"],
    [ContentTab, "content"],
    [SourcesTab, "sources"],
    [AiUsageTab, "ai-usage"],
  ])("shows a public backend failure on the %s tab", async (Tab, suffix) => {
    stubApi();
    failing = `/api/analytics/${suffix}`;
    renderWithProviders(<Tab filters={filters} />);
    expect(await screen.findByText("Telemetry temporarily unavailable")).toBeInTheDocument();
  });
});
