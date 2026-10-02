import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, screen, within } from "@testing-library/react";
import { DeliveryPage } from "../routes/delivery";
import { renderWithProviders } from "../test-utils";

interface TestResponse { ok: boolean; status: number; text: () => Promise<string> }
function reply(body: unknown, status = 200): TestResponse {
  return { ok: status < 400, status, text: async () => JSON.stringify(body) };
}
const run = (id: string, status: "success" | "failed" | "running", telegram_sent: number, started_at: string | null = "2026-09-01T12:00:00Z") => ({
  id, status, telegram_sent, started_at, task_id: null, articles_fetched: 1, summaries_generated: 1, error: null, finished_at: null,
});

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("Telegram delivery", () => {
  it("shows loading, then an empty delivery board with zero counts", async () => {
    let complete!: (value: TestResponse) => void;
    const fetch = vi.fn().mockImplementation(() => new Promise<TestResponse>((resolve) => { complete = resolve; }));
    vi.stubGlobal("fetch", fetch);
    const { container } = renderWithProviders(<DeliveryPage />);
    expect(container.querySelector(".mantine-Loader-root")).toBeInTheDocument();
    expect(screen.queryByText("No Telegram deliveries yet")).not.toBeInTheDocument();
    complete(reply({ runs: [] }));
    expect(await screen.findByText("No Telegram deliveries yet")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/api/runs", undefined);
    for (const label of ["Delivery attempts", "Delivered", "Needs attention"]) {
      expect(screen.getByText(label).parentElement).toHaveTextContent("0");
    }
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("counts delivered and failed runs separately and shows each delivery status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reply({ runs: [
      run("sent", "success", 1), run("failed", "failed", 0, null), run("pending", "running", 0),
    ] })));
    renderWithProviders(<DeliveryPage />);
    const rows = await screen.findAllByRole("row");
    expect(rows).toHaveLength(4);
    expect(screen.getByText("Delivery attempts").parentElement).toHaveTextContent("3");
    expect(screen.getByText("Delivered", { selector: "p" }).parentElement).toHaveTextContent("1");
    expect(screen.getByText("Needs attention").parentElement).toHaveTextContent("1");
    expect(within(rows[1]).getByText("Delivered")).toBeInTheDocument();
    expect(within(rows[1]).getByText("success")).toBeInTheDocument();
    expect(within(rows[2]).getByText("failed")).toBeInTheDocument();
    expect(within(rows[2]).getByText("Not delivered")).toBeInTheDocument();
    expect(within(rows[2]).getByText("-")).toBeInTheDocument();
    expect(within(rows[3]).getByText("running")).toBeInTheDocument();
    expect(within(rows[3]).getByText("Not delivered")).toBeInTheDocument();
  });
  it("surfaces request errors instead of claiming no deliveries", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reply({ detail: "Delivery history unavailable" }, 503)));
    renderWithProviders(<DeliveryPage />);
    expect(await screen.findByText("Delivery history unavailable")).toBeInTheDocument();
    expect(screen.queryByText("No Telegram deliveries yet")).not.toBeInTheDocument();
  });
});
