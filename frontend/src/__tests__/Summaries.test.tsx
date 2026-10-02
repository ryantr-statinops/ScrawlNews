import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, screen, within } from "@testing-library/react";
import { SummariesPage } from "../routes/summaries";
import { renderWithProviders } from "../test-utils";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

interface TestResponse { ok: boolean; status: number; text: () => Promise<string> }

function reply(body: unknown, status = 200): TestResponse {
  return { ok: status < 400, status, text: async () => JSON.stringify(body) };
}

describe("Summaries", () => {
  it("shows loading before the request resolves, then an empty result", async () => {
    let complete!: (value: TestResponse) => void;
    const fetch = vi.fn().mockImplementation(() => new Promise<TestResponse>((resolve) => { complete = resolve; }));
    vi.stubGlobal("fetch", fetch);
    const { container } = renderWithProviders(<SummariesPage />);
    expect(screen.getByRole("heading", { name: "Summaries" })).toBeInTheDocument();
    expect(container.querySelector(".mantine-Loader-root")).toBeInTheDocument();
    expect(screen.queryByText("No data")).not.toBeInTheDocument();
    complete(reply({ summaries: [] }));
    expect(await screen.findByText("No data")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/api/summaries?limit=20", undefined);
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows summary rows with abbreviated article ID and preview text", async () => {
    const summary = "An article summary with enough detail to exceed the preview boundary. ".repeat(3);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reply({ summaries: [
      { id: "one", article_id: "12345678-rest-of-id", summary_text: summary, model_used: "gemini-2.0", created_at: null },
      { id: "two", article_id: "short", summary_text: "Second story", model_used: "gpt-4o", created_at: null },
    ] })));
    renderWithProviders(<SummariesPage />);
    const rows = await screen.findAllByRole("row");
    expect(rows).toHaveLength(3);
    expect(within(rows[1]).getByText("12345678")).toBeInTheDocument();
    expect(within(rows[1]).getByText(summary.slice(0, 120))).toBeInTheDocument();
    expect(screen.queryByText("12345678-rest-of-id")).not.toBeInTheDocument();
    expect(screen.queryByText(summary)).not.toBeInTheDocument();
    expect(within(rows[1]).getByText("gemini-2.0")).toBeInTheDocument();
    expect(within(rows[2]).getByText("Second story")).toBeInTheDocument();
  });

  it("shows the backend error rather than an empty result", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reply({ error: "Summaries unavailable" }, 503)));
    renderWithProviders(<SummariesPage />);
    expect(await screen.findByText("Summaries unavailable")).toBeInTheDocument();
    expect(screen.queryByText("No data")).not.toBeInTheDocument();
  });
});
