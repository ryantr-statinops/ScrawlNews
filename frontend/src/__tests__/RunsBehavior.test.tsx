import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MantineProvider } from "@mantine/core";
import { RunsPage } from "../routes/runs";
import { theme } from "../theme";

interface MockResponse { ok: boolean; status: number; text: () => Promise<string> }
const response = (body: unknown, status = 200): MockResponse => ({ ok: status < 400, status, text: async () => JSON.stringify(body) });
function mount() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const view = render(<QueryClientProvider client={client}><MantineProvider theme={theme}><RunsPage /></MantineProvider></QueryClientProvider>);
  return { ...view, client };
}
afterEach(() => vi.unstubAllGlobals());

describe("Runs", () => {
  it("shows loading, then empty runs, and triggers using the configured limit before reflecting refreshed rows", async () => {
    let resolveRuns!: (value: MockResponse) => void;
    let reads = 0;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === "/api/config") return response({ fetch_limit: 37 });
      if (init?.method === "POST") return response({ task_id: "task", status: "pending", run_id: "run" });
      if (url === "/api/runs") {
        reads++;
        if (reads === 1) return new Promise<MockResponse>((resolve) => { resolveRuns = resolve; });
        return response({ runs: [{ id: "abc12345-6789", status: "success", articles_fetched: 8, summaries_generated: 3, telegram_sent: 1, started_at: "2026-09-10T00:00:00Z", error: null }] });
      }
      throw new Error(`Unexpected request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);
    mount();
    expect(document.querySelector(".mantine-Loader-root")).toBeInTheDocument();
    resolveRuns(response({ runs: [] }));
    expect(await screen.findByText("No runs yet")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("textbox", { name: "Fetch limit" })).toHaveAttribute("placeholder", "37"));
    fireEvent.click(screen.getByRole("button", { name: "Run Now" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/runs?fetch_limit=37", { method: "POST" }));
    const row = await screen.findByRole("row", { name: /abc12345 success 8 3 Yes/ });
    expect(within(row).getByText("abc12345")).toBeInTheDocument();
    expect(screen.queryByText("No runs yet")).not.toBeInTheDocument();
    expect(reads).toBe(2);
  });

  it("uses the displayed fallback limit when config fails and honors a custom limit", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (String(input) === "/api/config") return response({ error: "Config unavailable" }, 503);
      if (init?.method === "POST") return response({ task_id: "t", status: "pending", run_id: "r" });
      return response({ runs: [] });
    });
    vi.stubGlobal("fetch", fetchMock);
    mount();
    await screen.findByText("No runs yet");
    await waitFor(() => expect(screen.getByRole("textbox", { name: "Fetch limit" })).toHaveAttribute("placeholder", "20"));
    fireEvent.click(screen.getByRole("button", { name: "Run Now" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/runs?fetch_limit=20", { method: "POST" }));
    fireEvent.change(screen.getByRole("textbox", { name: "Fetch limit" }), { target: { value: "12" } });
    fireEvent.click(screen.getByRole("button", { name: "Run Now" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/runs?fetch_limit=12", { method: "POST" }));
  });

  it("shows a fetch failure instead of an empty board", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => String(input) === "/api/runs" ? response({ error: "Runs unavailable" }, 503) : response({ fetch_limit: 20 })));
    mount();
    expect(await screen.findByText("Runs unavailable")).toBeInTheDocument();
    expect(screen.queryByText("No runs yet")).not.toBeInTheDocument();
  });

  it("renders failed run details and absent counts distinctly", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => String(input) === "/api/runs" ? response({ runs: [{ id: "deadbeef-1", status: "failed", articles_fetched: null, summaries_generated: null, telegram_sent: 0, started_at: null, error: "RSS timed out" }] }) : response({ fetch_limit: 20 })));
    mount();
    const row = await screen.findByRole("row", { name: /deadbeef failed 0 0 No - RSS timed out/ });
    expect(within(row).getByText("RSS timed out")).toBeInTheDocument();
  });
});
