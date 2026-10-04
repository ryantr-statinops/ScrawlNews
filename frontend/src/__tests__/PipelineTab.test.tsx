import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { renderWithProviders } from "../test-utils";
import { PipelineTab } from "../features/analytics/PipelineTab";
import type { AnalyticsFiltersState, AnalyticsPeriod, PipelineResponse } from "../features/analytics/types";

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

const filters: AnalyticsFiltersState = {
  window: "24h",
  category: null,
  sourceId: null,
  provider: null,
  model: null,
};

const period: AnalyticsPeriod = {
  window: "24h",
  timezone: "Asia/Ho_Chi_Minh",
  current: { from: "2026-09-10T00:00:00Z", to: "2026-09-10T12:00:00Z" },
  previous: { from: "2026-09-09T12:00:00Z", to: "2026-09-10T00:00:00Z" },
};

const metric = (current: number, delta = 0) => ({
  current,
  previous: current,
  delta,
  delta_percent: delta === 0 ? null : 100,
});

function pipelineBody(overrides: Partial<PipelineResponse> = {}): PipelineResponse {
  return {
    period,
    kpis: {
      runs: metric(3, 1),
      success_rate: metric(92.5),
      throughput: metric(12),
      median_duration_seconds: metric(42),
      p95_duration_seconds: metric(120),
    },
    stages: [],
    errors: [],
    runs: [],
    ...overrides,
  };
}

vi.mock("../components/charts/BarChart", () => ({ BarChart: () => null }));

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.replaceState(null, "", "/analytics");
});

function stubPipeline(respond: (url: string) => MockResponse | undefined) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    const hit = respond(url);
    if (hit) return hit;
    throw new Error(`Unexpected request: ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("pipeline tab", () => {
  it("shows a loading indicator and then an empty pipeline for a window without telemetry", async () => {
    stubPipeline((url) =>
      url === "/api/analytics/pipeline?window=24h" ? response(pipelineBody()) : undefined,
    );
    renderWithProviders(<PipelineTab filters={filters} />);
    expect(document.querySelector(".mantine-Loader-root")).toBeInTheDocument();

    expect(await screen.findByText("No stage telemetry yet. The next pipeline run will establish timing baselines.")).toBeInTheDocument();
    expect(screen.getByText("No pipeline runs in this window.")).toBeInTheDocument();
    expect(screen.getByText("No stage errors recorded.")).toBeInTheDocument();
  });

  it("renders stage timings, runs and the error breakdown with formatted metrics", async () => {
    stubPipeline((url) =>
      url === "/api/analytics/pipeline?window=24h"
        ? response(
            pipelineBody({
              stages: [{ stage: "fetch", calls: 10, median_seconds: 1.25, p95_seconds: 3.5, items: 40, failures: 1 }],
              runs: [
                { id: "abcdef1234567890", status: "success", articles_fetched: 8, started_at: "2026-09-10T00:00:00Z" },
                { id: "ffff0000aaaa1111", status: "failed", started_at: null },
              ],
              errors: [{ stage: "summarize", error_class: "TimeoutError", count: 3 }],
            }),
          )
        : undefined,
    );
    renderWithProviders(<PipelineTab filters={filters} />);
    expect(await screen.findByText("Stage duration")).toBeInTheDocument();
    expect(screen.getByText("92.5%")).toBeInTheDocument();
    expect(screen.getByText("42.0s")).toBeInTheDocument();
    expect(screen.getByText("120.0s")).toBeInTheDocument();

    const runRows = screen.getAllByRole("row").filter((row) => /success|failed/.test(row.textContent ?? ""));
    expect(within(runRows[0]).getByText("abcdef12")).toBeInTheDocument();
    expect(within(runRows[0]).getByText("8")).toBeInTheDocument();
    expect(within(runRows[1]).getByText("—")).toBeInTheDocument();
    expect(within(runRows[1]).getByText("0")).toBeInTheDocument();

    const errorTable = screen.getByText("Error breakdown").closest("section, .mantine-Card-root") as HTMLElement;
    expect(within(errorTable).getByText("summarize")).toBeInTheDocument();
    expect(within(errorTable).getByText("TimeoutError")).toBeInTheDocument();
  });

  it("reports a failed pipeline request", async () => {
    stubPipeline((url) =>
      url === "/api/analytics/pipeline?window=24h"
        ? response({ error: "Pipeline telemetry unavailable" }, 503)
        : undefined,
    );
    renderWithProviders(<PipelineTab filters={filters} />);
    expect(await screen.findByText("Pipeline telemetry unavailable")).toBeInTheDocument();
  });

  it("opens the stage drill-down drawer for a KPI and for a run row", async () => {
    const fetchMock = stubPipeline((url) => {
      if (url === "/api/analytics/pipeline?window=24h") {
        return response(pipelineBody({ runs: [{ id: "abcdef1234567890", status: "pending", articles_fetched: null, started_at: "2026-09-10T00:00:00Z" }] }));
      }
      if (url.startsWith("/api/analytics/drilldown")) {
        return response({ period, kind: "stages", records: [{ stage: "fetch", calls: 4 }] });
      }
      return undefined;
    });
    renderWithProviders(<PipelineTab filters={filters} />);
    await screen.findByText("Stage duration");

    fireEvent.click(screen.getByRole("button", { name: "Inspect Runs" }));
    const panel = within(await screen.findByRole("dialog"));
    expect(await panel.findByRole("link", { name: "Open Runs" })).toHaveAttribute("href", "/runs");
    expect(panel.getByText("Showing 1 records")).toBeInTheDocument();
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/analytics/drilldown?window=24h&kind=runs",
        undefined,
      ),
    );

    fireEvent.click(screen.getByRole("button", { name: "Inspect P95 duration" }));
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/analytics/drilldown?window=24h&kind=stages",
        undefined,
      ),
    );
    expect(screen.queryByRole("link", { name: "Open Runs" })).not.toBeInTheDocument();

    fireEvent.click(screen.getByText("abcdef12"));
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/analytics/drilldown?window=24h&kind=stages&run_id=abcdef1234567890",
        undefined,
      ),
    );
  });
});
