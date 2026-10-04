import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { renderWithProviders } from "../test-utils";
import { AnalyticsDrawer } from "../features/analytics/AnalyticsDrawer";
import { AnalyticsFilters } from "../features/analytics/AnalyticsFilters";
import { AnalyticsPage } from "../routes/analytics";
import type { AnalyticsFiltersState } from "../features/analytics/types";

interface MockResponse {
  ok: boolean;
  status: number;
  text: () => Promise<string>;
}

const response = (body: unknown, status = 200): MockResponse => ({
  ok: status < 400,
  status,
  text: async () => JSON.stringify(body),
});

const period = {
  window: "24h",
  timezone: "Asia/Ho_Chi_Minh",
  current: { from: "2026-09-10T00:00:00Z", to: "2026-09-10T12:00:00Z" },
  previous: { from: "2026-09-09T12:00:00Z", to: "2026-09-10T00:00:00Z" },
};

const metric = { current: 4, previous: 2, delta: 2, delta_percent: 100 };

const aiUsageKpis = {
  total_tokens: metric,
  input_tokens: metric,
  output_tokens: metric,
  requests: metric,
  failure_rate: metric,
  median_latency_ms: metric,
  p95_latency_ms: metric,
};

// The real Mantine Select hangs in jsdom once its dropdown is opened, so the
// filter tests drive an injected native select that keeps the same
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
      allowDeselect?: boolean;
      onChange?: (value: string | null) => void;
    }) => {
      const data = Array.isArray(props.data) ? props.data : [];
      const options = data.map((item) =>
        typeof item === "string" ? { value: item, label: item } : item,
      );
      return (
        <select
          aria-label={String(props.label ?? "filter")}
          value={props.value ?? ""}
          onChange={(event) =>
            props.onChange?.(event.target.value === "" ? null : event.target.value)
          }
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

vi.mock("../components/charts/BarChart", () => ({ BarChart: () => null }));
vi.mock("../components/charts/DonutChart", () => ({ DonutChart: () => null }));

const filters: AnalyticsFiltersState = {
  window: "24h",
  category: null,
  sourceId: null,
  provider: null,
  model: null,
};

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.replaceState(null, "", "/analytics");
});

function stubApi(respond: (url: string, init?: RequestInit) => MockResponse | undefined) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const hit = respond(url, init);
    if (hit) return hit;
    throw new Error(`Unexpected request: ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

const emptyRows = {
  categories: [],
  sources: [],
  providers: [],
  models: [],
};

function analyticsApi(overrides: (url: string) => MockResponse | undefined = () => undefined) {
  return (url: string): MockResponse => {
    if (url.startsWith("/api/analytics/content")) {
      return response({
        period,
        velocity: [],
        categories: [{ category: "world", ...metric }],
        sources: [{ source: "Daily/VN", ...metric }],
        diversity: 0.5,
        freshness: {},
      });
    }
    if (url.startsWith("/api/analytics/ai-usage")) {
      return response({
        period,
        cost: {
          window_estimated_usd: 1,
          month_to_date_usd: 2,
          monthly_estimate_usd: 3,
          monthly_budget_usd: 4,
          budget_usage_percent: 75,
          alert: false,
          pricing_complete: true,
          unpriced_tokens: 0,
          unpriced_models: [],
        },
        kpis: aiUsageKpis,
        trend: [],
        providers: [{ provider: "azure/openai", ...metric }],
        models: [{ model: "gpt+4", ...metric }],
        operations: [],
      });
    }
    return overrides(url) ?? response({ error: `unhandled ${url}` }, 404);
  };
}

describe("analytics filters", () => {
  it("publishes each control change to the parent filter state", () => {
    const onChange = vi.fn();
    renderWithProviders(
      <AnalyticsFilters
        value={filters}
        onChange={onChange}
        categories={["world", "science"]}
        sources={["Daily/VN"]}
        providers={["azure/openai"]}
        models={["gpt+4"]}
      />,
    );
    const group = screen.getByRole("group", { name: "Analytics filters" });
    expect(within(group).getByLabelText("Window")).toHaveValue("24h");
    expect([...within(group).getByLabelText<HTMLSelectElement>("Category").options].map((o) => o.value)).toEqual(["", "world", "science"]);
    expect([...within(group).getByLabelText<HTMLSelectElement>("Source").options].map((o) => o.value)).toEqual(["", "Daily/VN"]);
    expect([...within(group).getByLabelText<HTMLSelectElement>("Provider").options].map((o) => o.value)).toEqual(["", "azure/openai"]);
    expect([...within(group).getByLabelText<HTMLSelectElement>("Model").options].map((o) => o.value)).toEqual(["", "gpt+4"]);

    fireEvent.change(within(group).getByLabelText("Window"), { target: { value: "7d" } });
    expect(onChange).toHaveBeenLastCalledWith({ ...filters, window: "7d" });

    fireEvent.change(within(group).getByLabelText("Category"), { target: { value: "science" } });
    expect(onChange).toHaveBeenLastCalledWith({ ...filters, category: "science" });

    fireEvent.change(within(group).getByLabelText("Source"), { target: { value: "Daily/VN" } });
    expect(onChange).toHaveBeenLastCalledWith({ ...filters, sourceId: "Daily/VN" });

    fireEvent.change(within(group).getByLabelText("Provider"), { target: { value: "azure/openai" } });
    expect(onChange).toHaveBeenLastCalledWith({ ...filters, provider: "azure/openai" });

    fireEvent.change(within(group).getByLabelText("Model"), { target: { value: "gpt+4" } });
    expect(onChange).toHaveBeenLastCalledWith({ ...filters, model: "gpt+4" });

    fireEvent.change(within(group).getByLabelText("Category"), { target: { value: "" } });
    expect(onChange).toHaveBeenLastCalledWith({ ...filters, category: null });
  });

  it("keeps the window selection when the select emits a null value", () => {
    const onChange = vi.fn();
    renderWithProviders(
      <AnalyticsFilters value={filters} onChange={onChange} categories={[]} sources={[]} providers={[]} models={[]} />,
    );
    fireEvent.change(screen.getByLabelText("Window"), { target: { value: "" } });
    expect(onChange).toHaveBeenCalledWith({ ...filters, window: "24h" });
  });
});

describe("analytics drawer", () => {
  it("stays closed until a selection is made", () => {
    stubApi(() => undefined);
    renderWithProviders(<AnalyticsDrawer selection={null} filters={filters} onClose={vi.fn()} />);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders drill-down records with an article link and a record count", async () => {
    const fetchMock = stubApi((url) => {
      if (url.startsWith("/api/analytics/drilldown")) {
        return response({
          period,
          kind: "articles",
          records: [
            { id: 1, title: "First", url: "https://example.com/first", score: 0.9 },
            { id: 2, title: "Second", url: null, score: null },
          ],
        });
      }
      return undefined;
    });
    renderWithProviders(
      <AnalyticsDrawer
        selection={{ title: "Top articles", kind: "articles" }}
        filters={filters}
        onClose={vi.fn()}
      />,
    );
    const panel = within(await screen.findByRole("dialog"));
    expect(await panel.findByRole("link", { name: "Open article" })).toHaveAttribute(
      "href",
      "https://example.com/first",
    );
    expect(panel.getByText("Showing 2 records")).toBeInTheDocument();
    expect(panel.getByText("score")).toBeInTheDocument();
    expect(panel.getAllByText("—")).toHaveLength(2);
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/analytics/drilldown?window=24h&kind=articles",
        undefined,
      ),
    );
  });

  it("offers a shortcut link for the related record list", async () => {
    stubApi((url) =>
      url.startsWith("/api/analytics/drilldown")
        ? response({ period, kind: "runs", records: [{ run_id: "r1", status: "success" }] })
        : undefined,
    );
    renderWithProviders(
      <AnalyticsDrawer
        selection={{ title: "Pipeline runs", kind: "runs", href: "/runs", hrefLabel: "Open Runs" }}
        filters={filters}
        onClose={vi.fn()}
      />,
    );
    const panel = within(await screen.findByRole("dialog"));
    expect(await panel.findByRole("link", { name: "Open Runs" })).toHaveAttribute("href", "/runs");
    expect(panel.getByText("run id")).toBeInTheDocument();
  });

  it("uses the default shortcut label when none is supplied", async () => {
    stubApi((url) =>
      url.startsWith("/api/analytics/drilldown") ? response({ period, kind: "runs", records: [] }) : undefined,
    );
    renderWithProviders(
      <AnalyticsDrawer selection={{ title: "Runs", kind: "runs", href: "/runs" }} filters={filters} onClose={vi.fn()} />,
    );
    expect(await screen.findByRole("link", { name: "Open related records" })).toBeInTheDocument();
    expect(await screen.findByText("No records in this period.")).toBeInTheDocument();
  });

  it("reports a failed drill-down request and closes through the callback", async () => {
    const onClose = vi.fn();
    stubApi((url) =>
      url.startsWith("/api/analytics/drilldown") ? response({ error: "Drilldown unavailable" }, 503) : undefined,
    );
    renderWithProviders(
      <AnalyticsDrawer selection={{ title: "Sources", kind: "sources" }} filters={filters} onClose={onClose} />,
    );
    expect(await screen.findByText("Drilldown unavailable")).toBeInTheDocument();
    fireEvent.click(document.querySelector(".mantine-Drawer-close") as HTMLElement);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("forwards the selected run id to the drill-down request", async () => {
    const fetchMock = stubApi((url) =>
      url.startsWith("/api/analytics/drilldown")
        ? response({ period, kind: "stages", records: [] })
        : undefined,
    );
    renderWithProviders(
      <AnalyticsDrawer
        selection={{ title: "Run abc", kind: "stages", params: { run_id: "abc" } }}
        filters={{ ...filters, window: "7d", category: "world", model: "gpt+4" }}
        onClose={vi.fn()}
      />,
    );
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/analytics/drilldown?window=7d&kind=stages&run_id=abc&category=world&model=gpt%2B4",
        undefined,
      ),
    );
  });
});

describe("analytics page", () => {
  it("renders the tab bar, seeds the filters from content and usage responses, and switches tabs", async () => {
    const fetchMock = stubApi(analyticsApi());
    renderWithProviders(<AnalyticsPage />);

    expect(screen.getByRole("heading", { name: "Insights" })).toBeInTheDocument();
    for (const tab of ["Overview", "News insights", "Sources", "AI Usage"]) {
      expect(screen.getByRole("tab", { name: tab })).toBeInTheDocument();
    }

    await waitFor(() =>
      expect([...screen.getByLabelText<HTMLSelectElement>("Category").options].map((o) => o.value)).toEqual(["", "world"]),
    );
    expect([...screen.getByLabelText<HTMLSelectElement>("Source").options].map((o) => o.value)).toEqual(["", "Daily/VN"]);
    expect([...screen.getByLabelText<HTMLSelectElement>("Provider").options].map((o) => o.value)).toEqual(["", "azure/openai"]);
    expect([...screen.getByLabelText<HTMLSelectElement>("Model").options].map((o) => o.value)).toEqual(["", "gpt+4"]);

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith("/api/analytics/content?window=24h", undefined),
    );
    expect(fetchMock).toHaveBeenCalledWith("/api/analytics/ai-usage?window=24h", undefined);

    fireEvent.click(screen.getByRole("tab", { name: "AI Usage" }));
    await waitFor(() =>
      expect(new URLSearchParams(window.location.search).get("tab")).toBe("ai-usage"),
    );
  });

  it("requests the content and usage endpoints again after a filter change", async () => {
    const fetchMock = stubApi(analyticsApi());
    renderWithProviders(<AnalyticsPage />);
    await waitFor(() =>
      expect([...screen.getByLabelText<HTMLSelectElement>("Category").options].map((o) => o.value)).toEqual(["", "world"]),
    );
    fireEvent.change(screen.getByLabelText("Category"), { target: { value: "world" } });
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith("/api/analytics/content?window=24h&category=world", undefined),
    );
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith("/api/analytics/ai-usage?window=24h&category=world", undefined),
    );
  });

  it("still renders the shell when the filter seed requests fail", async () => {
    stubApi((url) =>
      url.startsWith("/api/analytics/content") || url.startsWith("/api/analytics/ai-usage")
        ? response({ error: "Telemetry offline" }, 503)
        : response({ error: "unexpected" }, 404),
    );
    renderWithProviders(<AnalyticsPage />);
    await waitFor(() => expect(screen.getByLabelText("Category")).toHaveValue(""));
    expect([...screen.getByLabelText<HTMLSelectElement>("Category").options].map((o) => o.value)).toEqual([""]);
    expect(screen.getByRole("heading", { name: "Insights" })).toBeInTheDocument();
  });
});
