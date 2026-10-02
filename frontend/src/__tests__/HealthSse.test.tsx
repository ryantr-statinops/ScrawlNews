import { afterEach, describe, expect, it, vi } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MantineProvider } from "@mantine/core";
import { HealthPage } from "../routes/health";
import { theme } from "../theme";

class Stream {
  static instances: Stream[] = [];
  onmessage: ((event: MessageEvent) => void) | null = null;
  close = vi.fn();
  constructor(readonly url: string) { Stream.instances.push(this); }
  send(data: string) { this.onmessage?.({ data } as MessageEvent); }
}
const response = (body: unknown, status = 200) => ({ ok: status < 400, status, text: async () => JSON.stringify(body) });
function mount() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}><MantineProvider theme={theme}><HealthPage /></MantineProvider></QueryClientProvider>);
}
afterEach(() => { vi.unstubAllGlobals(); Stream.instances = []; });

describe("Health board and stream", () => {
  it("shows DB/Redis readiness, failed runs only, then live messages and closes the stream on exit", async () => {
    vi.stubGlobal("EventSource", Stream);
    vi.stubGlobal("fetch", vi.fn(async (url: RequestInfo | URL) => String(url) === "/health"
      ? response({ status: "degraded", db: "ok", redis: "unavailable" })
      : response({ runs: [
        { id: "failed01-xxx", status: "failed", error: "Redis timeout" },
        { id: "success1-xxx", status: "success", error: null },
      ] })));
    const view = mount();
    expect(document.querySelector(".mantine-Loader-root")).toBeInTheDocument();
    expect(await screen.findByText(/status: degraded · db: ok · redis: unavailable/)).toBeInTheDocument();
    expect(await screen.findByText("Error board (1 failed runs)")).toBeInTheDocument();
    expect(screen.getByText("failed01")).toBeInTheDocument();
    expect(screen.getByText("Redis timeout")).toBeInTheDocument();
    expect(screen.queryByText("success1")).not.toBeInTheDocument();
    expect(screen.getByText("waiting for stream...")).toBeInTheDocument();
    expect(Stream.instances[0].url).toBe("/api/logs/stream");
    act(() => Stream.instances[0].send("worker started"));
    expect(screen.getByText("worker started")).toBeInTheDocument();
    act(() => Stream.instances[0].send("pipeline complete"));
    expect(screen.getByText("Live logs (SSE)").nextElementSibling).toHaveTextContent("worker started pipeline complete");
    view.unmount();
    expect(Stream.instances[0].close).toHaveBeenCalledOnce();
  });

  it("displays health errors while retaining the empty failure board", async () => {
    vi.stubGlobal("EventSource", Stream);
    vi.stubGlobal("fetch", vi.fn(async (url: RequestInfo | URL) => String(url) === "/health" ? response({ error: "Health unavailable" }, 503) : response({ runs: [] })));
    mount();
    expect(await screen.findByText("Health unavailable")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("No failures")).toBeInTheDocument());
    expect(screen.queryByText(/status: /)).not.toBeInTheDocument();
  });
});
