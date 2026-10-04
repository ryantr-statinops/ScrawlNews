import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, screen, waitFor } from "@testing-library/react";
import { AgentPage } from "../routes/agent";
import { renderWithProviders } from "../test-utils";
import type { AgentDecision } from "../types/api";

const json = (body: unknown) => ({ ok: true, status: 200, text: async () => JSON.stringify(body) });
const calls: Array<{ url: string; init?: RequestInit }> = [];
let decision: AgentDecision;
function mount() {
  calls.length = 0;
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    calls.push({ url, init });
    if (url === "/api/agent/run") return json({ decision });
    return json({ correlation_id: decision.correlation_id, status: "approved", executed: true });
  }));
  renderWithProviders(<AgentPage />);
}
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("assistant approval boundary", () => {
  it("blocks empty requests and never offers approval for a blocked decision", async () => {
    decision = { status: "blocked", reason: "This request is not permitted", action: null, correlation_id: "blocked/id" };
    mount();
    const request = screen.getByRole("textbox", { name: "Request" });
    fireEvent.change(request, { target: { value: "   " } });
    expect(screen.getByRole("button", { name: "Ask Agent" })).toBeDisabled();
    expect(calls).toHaveLength(0);

    fireEvent.change(request, { target: { value: "delete everything" } });
    fireEvent.click(screen.getByRole("button", { name: "Ask Agent" }));
    expect(await screen.findByText("This request is not permitted")).toBeInTheDocument();
    expect(screen.getByText("blocked")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Approve action" })).not.toBeInTheDocument();
    expect(JSON.parse(String(calls[0].init?.body))).toEqual({ request: "delete everything" });
    expect(calls).toHaveLength(1);
  });

  it("approves only the URL-encoded correlation ID returned by the pending decision", async () => {
    decision = { status: "pending_approval", reason: "Backup needs your approval", action: null, correlation_id: "run/42+approval" };
    mount();
    fireEvent.click(screen.getByRole("button", { name: "Ask Agent" }));
    expect(await screen.findByText("Backup needs your approval")).toBeInTheDocument();
    expect(screen.getByText("pending_approval")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Approve action" }));
    await waitFor(() => expect(calls).toHaveLength(2));
    expect(calls[1].url).toBe("/api/agent/approve/run%2F42%2Bapproval");
    expect(calls[1].init?.method).toBe("POST");
    expect(calls[1].init?.body).toBeUndefined();
  });
});
