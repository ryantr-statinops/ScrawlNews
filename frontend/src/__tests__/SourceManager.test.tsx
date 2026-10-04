import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { renderWithProviders } from "../test-utils";
import { SourceManager } from "../components/SourceManager";

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

const sources = [
  { id: "s1", name: "Example", url: "https://example.com/rss", category: "technology", enabled: 1 },
  { id: "s2", name: "Custom", url: "https://custom.example/feed", category: null, enabled: 0 },
];

afterEach(() => {
  vi.unstubAllGlobals();
});

type Responder = (url: string, init?: RequestInit) => MockResponse | undefined;

function stubApi(respond: Responder) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const hit = respond(url, init);
    if (hit) return hit;
    throw new Error(`Unexpected request: ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("source manager", () => {
  it("lists the catalog with the category fallback and enabled state", async () => {
    stubApi((url) => (url === "/api/sources" ? response({ sources }) : undefined));
    renderWithProviders(<SourceManager />);
    expect(await screen.findByText("Example")).toBeInTheDocument();
    const rows = screen.getAllByRole("row");
    expect(within(rows[1]).getByText("technology")).toBeInTheDocument();
    expect(within(rows[2]).getByText("custom")).toBeInTheDocument();
    const switches = screen.getAllByRole("switch") as HTMLInputElement[];
    expect(switches.map((input) => input.checked)).toEqual([true, false]);
  });

  it("filters the catalog with the search box", async () => {
    const fetchMock = stubApi((url) =>
      url.startsWith("/api/sources") ? response({ sources }) : undefined,
    );
    renderWithProviders(<SourceManager />);
    await screen.findByText("Example");
    fireEvent.change(screen.getByPlaceholderText("Search catalog"), { target: { value: "custom" } });
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith("/api/sources?q=custom", undefined),
    );
  });

  it("keeps the add control disabled until both a name and a URL are supplied", async () => {
    stubApi((url) => (url === "/api/sources" ? response({ sources: [] }) : undefined));
    renderWithProviders(<SourceManager />);
    const add = await screen.findByRole("button", { name: "Add" });
    expect(add).toBeDisabled();

    fireEvent.change(screen.getByPlaceholderText("Custom source name"), { target: { value: "Daily" } });
    expect(add).toBeDisabled();
    fireEvent.change(screen.getByPlaceholderText("RSS/Atom URL"), { target: { value: "https://daily.example/rss" } });
    expect(add).toBeEnabled();
  });

  it("creates a custom source, clears the form and reloads the catalog", async () => {
    let creates = 0;
    const fetchMock = stubApi((url, init) => {
      if (url === "/api/sources" && init?.method === "POST") {
        creates += 1;
        return response({ id: "s3", name: "Daily", url: "https://daily.example/rss", category: null, enabled: 1 });
      }
      if (url === "/api/sources") return response({ sources });
      return undefined;
    });
    renderWithProviders(<SourceManager />);
    const add = await screen.findByRole("button", { name: "Add" });
    fireEvent.change(screen.getByPlaceholderText("Custom source name"), { target: { value: "Daily" } });
    fireEvent.change(screen.getByPlaceholderText("RSS/Atom URL"), { target: { value: "https://daily.example/rss" } });
    fireEvent.click(add);

    await waitFor(() => expect(creates).toBe(1));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/sources",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ name: "Daily", url: "https://daily.example/rss", enabled: true }),
      }),
    );
    await waitFor(() => expect(screen.getByPlaceholderText("Custom source name")).toHaveValue(""));
    expect(screen.getByPlaceholderText("RSS/Atom URL")).toHaveValue("");
  });

  it("toggles a source and refreshes the catalog", async () => {
    const fetchMock = stubApi((url, init) => {
      if (url === "/api/sources/s1" && init?.method === "PUT") {
        return response({ updated: { enabled: "false" } });
      }
      if (url === "/api/sources") return response({ sources });
      return undefined;
    });
    renderWithProviders(<SourceManager />);
    await screen.findByText("Example");
    fireEvent.click(screen.getAllByRole("switch")[0]);
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/sources/s1",
        expect.objectContaining({ method: "PUT", body: JSON.stringify({ enabled: false }) }),
      ),
    );
  });

  it("runs a source connectivity test with the encoded identifier", async () => {
    let tested = "";
    const fetchMock = stubApi((url, init) => {
      if (url.startsWith("/api/sources/") && url.endsWith("/test")) {
        tested = url;
        return response({ ok: true });
      }
      if (url === "/api/sources") return response({ sources: [{ ...sources[0], id: "s/1" }] });
      return undefined;
    });
    renderWithProviders(<SourceManager />);
    await screen.findByText("Example");
    fireEvent.click(screen.getAllByRole("button", { name: "Test" })[0]);
    await waitFor(() => expect(tested).toBe("/api/sources/s%2F1/test"));
    expect(fetchMock).toHaveBeenCalledWith("/api/sources/s%2F1/test", { method: "POST" });
  });

  it("surfaces a catalog listing failure", async () => {
    stubApi((url) => (url === "/api/sources" ? response({ error: "Source catalog offline" }, 503) : undefined));
    renderWithProviders(<SourceManager />);
    expect(await screen.findByText("Source catalog offline")).toBeInTheDocument();
  });
});
