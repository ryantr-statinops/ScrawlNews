import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, screen, waitFor } from "@testing-library/react";
import { ConfigPage } from "../routes/config";
import { renderWithProviders } from "../test-utils";
import type { ConfigResponse } from "../types/api";

const baseConfig: ConfigResponse = {
  fetch_limit: 20,
  summary_lang: "vi",
  llm_provider: "openai",
  llm_model: "gpt-4o",
  llm_configured: true,
  llm_price_snapshot_json: "{}",
  llm_monthly_budget_usd: 0,
  telegram_enabled: false,
  telegram_configured: false,
  retention_days: 7,
  news_categories: "world",
  schedule_times: "08:00",
  schedule_timezone: "Asia/Ho_Chi_Minh",
  news_country: "VN",
  news_city: "Hanoi",
  log_level: "INFO",
};
const json = (body: unknown, status = 200) => ({ ok: status < 400, status, text: async () => JSON.stringify(body) });
const saves: Record<string, unknown>[] = [];
let reject = false;
let current: ConfigResponse = { ...baseConfig };
let configHistory = {
  history: [{ key: "schedule_times", old_value: "07:00", new_value: "08:00", changed_at: "2026-09-01T00:00:00Z" }],
};
function mount() {
  saves.length = 0;
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    if (url.startsWith("/api/config/history")) return json(configHistory);
    if (url === "/api/sources") return json({ sources: [] });
    if (init?.method === "PUT") {
      const body = JSON.parse(String(init.body)) as Record<string, unknown>;
      saves.push(body);
      if (reject) return json({ error: "Invalid configuration" }, 400);
      configHistory = {
        history: [
          { key: "schedule_times", old_value: current.schedule_times, new_value: String(body.schedule_times), changed_at: "2026-09-02T00:00:00Z" },
        ],
      };
      current = { ...current, ...body } as ConfigResponse;
      return json({ updated: body });
    }
    return json(current);
  }));
  renderWithProviders(<ConfigPage />);
}
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  reject = false;
  current = { ...baseConfig };
  configHistory = {
    history: [{ key: "schedule_times", old_value: "07:00", new_value: "08:00", changed_at: "2026-09-01T00:00:00Z" }],
  };
});

describe("settings validation and history", () => {
  it("rejects duplicate or empty schedules and out-of-range fetch limit/retention before any request", async () => {
    mount();
    const schedule = await screen.findByRole("textbox", { name: /Daily update times/i });

    fireEvent.change(schedule, { target: { value: "08:00,08:00" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Use unique HH:MM times separated by commas")).toBeInTheDocument();
    expect(saves).toHaveLength(0);

    fireEvent.change(schedule, { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(saves).toHaveLength(0);
    expect(screen.getByText("Use unique HH:MM times separated by commas")).toBeInTheDocument();

    fireEvent.change(schedule, { target: { value: "09:30" } });
    fireEvent.change(screen.getByRole("textbox", { name: "Fetch limit" }), { target: { value: "101" } });
    fireEvent.change(screen.getByRole("textbox", { name: "Retention days" }), { target: { value: "31" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Number must be less than or equal to 100")).toBeInTheDocument();
    expect(screen.getByText("Number must be less than or equal to 30")).toBeInTheDocument();
    expect(saves).toHaveLength(0);
  });

  it("sends the valid form payload and shows the refreshed preference history", async () => {
    mount();
    const schedule = await screen.findByRole("textbox", { name: /Daily update times/i });
    fireEvent.change(schedule, { target: { value: "09:30,18:45" } });
    fireEvent.change(screen.getByRole("textbox", { name: "Schedule timezone" }), { target: { value: "UTC" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() => expect(saves).toHaveLength(1));
    expect(saves[0]).toEqual({
      fetch_limit: 20,
      summary_lang: "vi",
      telegram_enabled: false,
      retention_days: 7,
      schedule_times: "09:30,18:45",
      schedule_timezone: "UTC",
      news_country: "VN",
      news_city: "Hanoi",
      llm_price_snapshot_json: "{}",
      llm_monthly_budget_usd: 0,
    });
    expect(schedule).toHaveValue("09:30,18:45");
    expect(await screen.findByText("09:30,18:45")).toBeInTheDocument();
    expect(screen.getByText("08:00")).toBeInTheDocument();
    expect(screen.queryByText("07:00")).not.toBeInTheDocument();
  });

  it("keeps the form values and shows the safe server error when the backend refuses the save", async () => {
    reject = true;
    mount();
    const schedule = await screen.findByRole("textbox", { name: /Daily update times/i });
    fireEvent.change(schedule, { target: { value: "10:00" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Invalid configuration")).toBeInTheDocument();
    expect(screen.getByText("Unable to save settings")).toBeInTheDocument();
    expect(schedule).toHaveValue("10:00");
    expect(saves).toHaveLength(1);
    expect(saves[0].schedule_times).toBe("10:00");
    expect(screen.getByText("08:00")).toBeInTheDocument();
  });
});
