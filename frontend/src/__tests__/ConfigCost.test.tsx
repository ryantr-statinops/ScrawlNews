import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MantineProvider } from "@mantine/core";
import { ConfigPage } from "../routes/config";
import { theme } from "../theme";
import type { ConfigResponse } from "../types/api";

const config: ConfigResponse = {
  fetch_limit: 37, summary_lang: "vi", llm_provider: "openai", llm_model: "gpt-4o", llm_configured: true,
  llm_price_snapshot_json: '{"openai/gpt-4o":{"input_per_million_usd":2,"output_per_million_usd":8}}',
  llm_monthly_budget_usd: 12.5, telegram_enabled: false, telegram_configured: false,
  retention_days: 7, news_categories: "world", schedule_times: "08:00", schedule_timezone: "Asia/Ho_Chi_Minh",
  news_country: "VN", news_city: "Hanoi", log_level: "INFO",
};
const json = (body: unknown, status = 200) => ({ ok: status < 400, status, text: async () => JSON.stringify(body) });
const requests: Array<{ url: string; body?: Record<string, unknown> }> = [];
let failSave = false;
let history = { history: [{ key: "llm_monthly_budget_usd", old_value: "0", new_value: "12.5", changed_at: "2026-09-01T00:00:00Z" }] };
function setup() {
  requests.length = 0;
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    if (url.startsWith("/api/config/history")) return json(history);
    if (url === "/api/sources") return json({ sources: [] });
    if (init?.method === "PUT") {
      const body = JSON.parse(String(init.body)) as Record<string, unknown>;
      requests.push({ url, body });
      if (failSave) return json({ error: "Invalid configuration" }, 400);
      history = { history: [{ key: "llm_monthly_budget_usd", old_value: "12.5", new_value: String(body.llm_monthly_budget_usd), changed_at: "2026-09-02T00:00:00Z" }] };
      return json({ updated: {} });
    }
    return json(config);
  }));
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={client}><MantineProvider theme={theme}><ConfigPage /></MantineProvider></QueryClientProvider>);
}
afterEach(() => { cleanup(); vi.unstubAllGlobals(); failSave = false; });

describe("pricing configuration", () => {
  it("loads server values, rejects malformed JSON, saves edited prices/budget and refreshes history", async () => {
    setup();
    const prices = await screen.findByRole("textbox", { name: /LLM price snapshot JSON/i });
    expect(prices).toHaveValue(config.llm_price_snapshot_json);
    expect(screen.getByRole("textbox", { name: "Fetch limit" })).toHaveValue("37");
    expect(screen.getByRole("textbox", { name: /Monthly AI budget/i })).toHaveValue("12.5");
    expect(screen.getByText("12.5")).toBeInTheDocument();
    fireEvent.change(prices, { target: { value: "not json" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Enter a JSON object of provider/model prices")).toBeInTheDocument();
    expect(requests).toHaveLength(0);
    const updated = '{"openai/gpt-4o":{"input_per_million_usd":3,"output_per_million_usd":9}}';
    fireEvent.change(prices, { target: { value: updated } });
    fireEvent.change(screen.getByRole("textbox", { name: /Monthly AI budget/i }), { target: { value: "18" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() => expect(requests).toHaveLength(1));
    expect(requests[0].body).toMatchObject({ fetch_limit: 37, llm_price_snapshot_json: updated, llm_monthly_budget_usd: 18 });
    expect(await screen.findByText("18")).toBeInTheDocument();
  });

  it("shows the backend error when a price snapshot save is refused", async () => {
    failSave = true;
    setup();
    await screen.findByRole("textbox", { name: /LLM price snapshot JSON/i });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Invalid configuration")).toBeInTheDocument();
  });
});
