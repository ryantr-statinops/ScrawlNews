import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MantineProvider } from "@mantine/core";
import { AiUsageTab } from "../features/analytics/AiUsageTab";
import { theme } from "../theme";
import type { AiUsageResponse, AnalyticsFiltersState } from "../features/analytics/types";

const filters: AnalyticsFiltersState = { window: "30d", category: null, sourceId: null, provider: null, model: null };
const metric = { current: 0, previous: 0, delta: 0, delta_percent: null };
const response: AiUsageResponse = {
  period: { window: "30d", timezone: "UTC", current: { from: "", to: "" }, previous: { from: "", to: "" } },
  kpis: { total_tokens: metric, input_tokens: metric, output_tokens: metric, requests: metric, failure_rate: metric, median_latency_ms: metric, p95_latency_ms: metric },
  trend: [], providers: [], models: [], operations: [],
  cost: { window_estimated_usd: 1.234567, month_to_date_usd: 2.5, monthly_estimate_usd: 9.876543, monthly_budget_usd: 8, budget_usage_percent: 123.5, alert: true, pricing_complete: true, unpriced_tokens: 0, unpriced_models: [] },
};

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
function renderUsage(cost: AiUsageResponse["cost"]) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, text: async () => JSON.stringify({ ...response, cost }) }));
  render(<QueryClientProvider client={client}><MantineProvider theme={theme}><AiUsageTab filters={filters} /></MantineProvider></QueryClientProvider>);
}

describe("AI usage cost guardrails", () => {
  it("shows actual priced costs and a non-blocking projected budget warning", async () => {
    renderUsage(response.cost);
    expect(await screen.findByRole("heading", { name: "$1.234567" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "$9.876543" })).toBeInTheDocument();
    expect(screen.getByText("Month to date: $2.500000")).toBeInTheDocument();
    expect(screen.getByText("Monthly AI budget warning")).toBeInTheDocument();
    expect(screen.getByText(/123.5% used/)).toBeInTheDocument();
    expect(screen.getByText(/AI calls continue/)).toBeInTheDocument();
  });

  it("identifies unpriced models and does not claim an exceeded budget", async () => {
    renderUsage({ ...response.cost, alert: false, pricing_complete: false, unpriced_tokens: 1250, unpriced_models: ["openai/gpt-4o", "other/model"] });
    expect(await screen.findByText("Pricing incomplete")).toBeInTheDocument();
    expect(screen.getByText(/openai\/gpt-4o, other\/model/)).toBeInTheDocument();
    expect(screen.getByText(/1,250 unpriced tokens/)).toBeInTheDocument();
    expect(screen.queryByText("Monthly AI budget warning")).not.toBeInTheDocument();
  });
});
