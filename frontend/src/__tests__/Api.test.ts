import { afterEach, describe, expect, it, vi } from "vitest";
import { createSource, fetchArticles, fetchDigestArticles, fetchDigests, fetchSources, fetchSummaries, requestJson, updateConfig, updateSource } from "../lib/api";

afterEach(() => vi.unstubAllGlobals());

function respond(body: unknown, status = 200) {
  return { ok: status >= 200 && status < 300, status, text: async () => JSON.stringify(body) };
}

describe("API requests", () => {
  it("encodes user-controlled filters and path segments without changing their meaning", async () => {
    const fetch = vi.fn().mockResolvedValue(respond({ articles: [] }));
    vi.stubGlobal("fetch", fetch);
    await fetchArticles({ category: "world & news", search: "Hà Nội? #1" });
    await fetchDigests("business & tech");
    await fetchSummaries("id/with?& space");
    await fetchDigestArticles("digest/one?two");
    await fetchSources("Việt Nam & world");
    const urls = fetch.mock.calls.map(([url]) => url as string);
    expect(new URL(urls[0], "http://localhost").searchParams.get("category")).toBe("world & news");
    expect(new URL(urls[0], "http://localhost").searchParams.get("search")).toBe("Hà Nội? #1");
    expect(new URL(urls[1], "http://localhost").searchParams.get("category")).toBe("business & tech");
    expect(new URL(urls[2], "http://localhost").searchParams.get("article_id")).toBe("id/with?& space");
    expect(new URL(urls[2], "http://localhost").searchParams.get("limit")).toBe("20");
    expect(urls[3]).toBe("/api/digests/digest%2Fone%3Ftwo/articles");
    expect(new URL(urls[4], "http://localhost").searchParams.get("q")).toBe("Việt Nam & world");
  });

  it("sends JSON mutations with encoded identifiers and returns server responses", async () => {
    const fetch = vi.fn().mockResolvedValueOnce(respond({ updated: { fetch_limit: "12" } }))
      .mockResolvedValueOnce(respond({ id: "source/1", name: "Daily" }))
      .mockResolvedValueOnce(respond({ id: "source/2", name: "Daily" }));
    vi.stubGlobal("fetch", fetch);
    await updateConfig({ fetch_limit: 12 });
    await updateSource("source/1", { name: "Daily" });
    await createSource({ name: "Daily" });
    expect(fetch.mock.calls[0]).toEqual(["/api/config", { method: "PUT", headers: { "Content-Type": "application/json" }, body: '{"fetch_limit":12}' }]);
    expect(fetch.mock.calls[1][0]).toBe("/api/sources/source%2F1");
    expect(fetch.mock.calls[1][1]).toMatchObject({ method: "PUT", body: '{"name":"Daily"}' });
    expect(fetch.mock.calls[2][1]).toMatchObject({ method: "POST", body: '{"name":"Daily"}' });
  });

  it.each([
    [{ error: "Invalid configuration" }, "Invalid configuration"],
    [{ detail: "Article not found" }, "Article not found"],
    [{ other: "ignored" }, "Request failed: 422"],
  ])("reports HTTP failures from the server safely: %j", async (body, message) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respond(body, 422)));
    await expect(requestJson("/api/articles")).rejects.toMatchObject({ name: "ApiError", status: 422, message, body });
  });

  it("does not mistake an HTML failure response for valid JSON", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 502, text: async () => "<html>private gateway detail</html>" }));
    await expect(requestJson("/api/articles")).rejects.toMatchObject({ name: "ApiError", status: 502, message: "Server returned invalid JSON" });
  });

});
