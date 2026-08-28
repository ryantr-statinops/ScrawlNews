import { describe, it, expect, vi } from "vitest";

const mockFetch = (data: unknown) =>
  Promise.resolve({
    json: () => Promise.resolve(data),
    ok: true,
  } as Response);

describe("API client", () => {
  it("fetchArticles returns data", async () => {
    global.fetch = vi.fn(() => mockFetch({ count: 1, articles: [] }));
    const { fetchArticles } = await import("../lib/api");
    const result = await fetchArticles();
    expect(result.count).toBe(1);
  });

  it("fetchRuns returns data", async () => {
    global.fetch = vi.fn(() => mockFetch({ runs: [] }));
    const { fetchRuns } = await import("../lib/api");
    const result = await fetchRuns();
    expect(result.runs).toEqual([]);
  });

  it("fetchConfig returns data", async () => {
    global.fetch = vi.fn(() => mockFetch({ fetch_limit: 20 }));
    const { fetchConfig } = await import("../lib/api");
    const result = await fetchConfig();
    expect(result.fetch_limit).toBe(20);
  });
});
