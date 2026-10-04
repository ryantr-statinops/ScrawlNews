import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { renderWithProviders } from "../test-utils";
import { FeedPage } from "../routes/index";
import { SettingsPage } from "../routes/settings";

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

const article = {
  id: "a1",
  title: "Article One",
  url: "https://example.com/one",
  source: "Example",
  category: "technology",
  content: "Body text",
  fetched_at: "2026-09-10T01:00:00Z",
  published_at: "2026-09-10T00:00:00Z",
  summarized: 1,
};

const digest = {
  id: "d1",
  category: "technology",
  title: "Latest digest",
  digest_text: "Digest body",
  article_count: 2,
  model_used: "gpt",
  status: "success",
  error: null,
  created_at: "2026-09-10T00:00:00Z",
};

const config = { fetch_limit: 37, news_categories: "technology, business ,world" };

// The real Mantine Select hangs in jsdom when its dropdown is opened, so the
// filter tests drive an injected native select that keeps the same
// value/onChange contract. No production code is modified.
vi.mock("@mantine/core", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@mantine/core")>();
  return {
    ...actual,
    Select: (props: {
      label?: unknown;
      value?: string | null;
      data?: Array<string | { value: string; label: string }>;
      placeholder?: string;
      clearable?: boolean;
      onChange?: (value: string | null) => void;
    }) => {
      const data = Array.isArray(props.data) ? props.data : [];
      const options = data.map((item) => (typeof item === "string" ? { value: item, label: item } : item));
      return (
        <select
          aria-label={String(props.label ?? "filter")}
          value={props.value ?? ""}
          onChange={(event) => props.onChange?.(event.target.value === "" ? null : event.target.value)}
        >
          <option value="">{props.placeholder ?? String(props.label ?? "")}</option>
          {options.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      );
    },
  };
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.replaceState(null, "", "/");
});

type StubResponse = MockResponse | Promise<MockResponse>;

function stubApi(overrides: (url: string, init?: RequestInit) => StubResponse | undefined) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const hit = overrides(url, init);
    if (hit) return hit;
    throw new Error(`Unexpected request: ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("Feed page", () => {
  it("loads the article feed, shows the empty state, and serializes submitted filters into the request", async () => {
    let resolveArticles!: (value: MockResponse) => void;
    const fetchMock = stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [digest] });
      if (url === "/api/runs") return response({ runs: [{ id: "r1", status: "success", articles_fetched: 4, started_at: "2026-09-10T00:00:00Z" }] });
      if (url === "/api/sources") return response({ sources: [{ id: "s1", name: "Example", url: "https://example.com/rss", category: "technology", enabled: 1 }] });
      if (url.startsWith("/api/articles")) return new Promise<MockResponse>((resolve) => { resolveArticles = resolve; });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    expect(document.querySelector(".mantine-Loader-root")).toBeInTheDocument();

    resolveArticles(response({ count: 0, articles: [] }));
    expect(await screen.findByText("No articles found")).toBeInTheDocument();
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/articles?limit=20&offset=0", undefined));
    expect(fetchMock).toHaveBeenCalledWith("/api/articles?limit=20&offset=0", undefined);
  });

  it("renders articles with their run status and applies search, category and date filters", async () => {
    const fetchMock = stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [digest] });
      if (url === "/api/runs") return response({ runs: [{ id: "r1", status: "success", articles_fetched: 4, started_at: "2026-09-10T00:00:00Z" }] });
      if (url === "/api/sources") return response({ sources: [{ id: "s1", name: "Example", url: "https://example.com/rss", category: "technology", enabled: 1 }] });
      if (url.startsWith("/api/articles?")) {
        if (url.includes("q=chip")) return response({ count: 1, articles: [article] });
        return response({ count: 0, articles: [] });
      }
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    expect(await screen.findByText("No articles found")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByLabelText("Articles per update")).toHaveAttribute("placeholder", "37"));
    expect(screen.getByText("Updated")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Update feed" })).toBeEnabled();

    fireEvent.change(screen.getByLabelText("Search"), { target: { value: "chip" } });
    fireEvent.keyDown(screen.getByLabelText("Search"), { key: "Enter" });
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/articles?limit=20&offset=0&q=chip",
        undefined,
      ),
    );

    expect(await screen.findByText("Article One")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("From"), { target: { value: "2026-09-01" } });
    fireEvent.change(screen.getByLabelText("To"), { target: { value: "2026-09-05" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/articles?limit=20&offset=0&q=chip&from=2026-09-01T00%3A00%3A00Z&to=2026-09-05T23%3A59%3A59Z",
        undefined,
      ),
    );
  });

  it("offers source and category filters derived from the config and source catalog", async () => {
    const fetchMock = stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [{ id: "s1", name: "Example", url: "https://example.com/rss", category: "technology", enabled: 1 }] });
      if (url.startsWith("/api/articles?")) return response({ count: 0, articles: [] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    await screen.findByText("No articles found");

    const source = screen.getByLabelText<HTMLSelectElement>("Source");
    expect([...source.options].map((option) => option.value)).toEqual(["", "Example"]);
    fireEvent.change(source, { target: { value: "Example" } });

    const category = screen.getByLabelText<HTMLSelectElement>("Category");
    expect([...category.options].map((option) => option.value)).toEqual(["", "technology", "business", "world"]);
    fireEvent.change(category, { target: { value: "business" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/articles?limit=20&offset=0&source=Example&category=business",
        undefined,
      ),
    );
  });

  it("triggers a feed update with the configured limit and surfaces a rejected run", async () => {
    const fetchMock = stubApi((url, init) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url.startsWith("/api/runs?") && init?.method === "POST") return response({ error: "Run already in progress" }, 409);
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 0, articles: [] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    await waitFor(() =>
      expect(screen.getByLabelText("Articles per update")).toHaveAttribute("placeholder", "37"),
    );
    fireEvent.click(screen.getByRole("button", { name: "Update feed" }));
    expect(await screen.findByText("Run already in progress")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/runs?fetch_limit=37", { method: "POST" });
  });

  it("keeps the update control disabled while a run is in flight", async () => {
    stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url === "/api/runs") return response({ runs: [{ id: "r1", status: "running", articles_fetched: 0, started_at: "2026-09-10T00:00:00Z" }] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 0, articles: [] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    expect(await screen.findByText("Updating")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Update feed" })).toBeDisabled();
  });

  it("honors a custom run limit and refreshes the feed once the run is accepted", async () => {
    let resolveRun!: (value: MockResponse) => void;
    const fetchMock = stubApi((url, init) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url.startsWith("/api/runs?") && init?.method === "POST") {
        return new Promise<MockResponse>((resolve) => { resolveRun = resolve; });
      }
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 0, articles: [] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    await screen.findByText("No articles found");
    await waitFor(() =>
      expect(screen.getByLabelText("Articles per update")).toHaveAttribute("placeholder", "37"),
    );
    expect(screen.getByRole("button", { name: "Update feed" })).toBeEnabled();

    fireEvent.change(screen.getByLabelText("Articles per update"), { target: { value: "12" } });
    fireEvent.click(screen.getByRole("button", { name: "Update feed" }));
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith("/api/runs?fetch_limit=12", { method: "POST" }),
    );
    expect(screen.getByRole("button", { name: "Update feed" })).toBeDisabled();

    const before = fetchMock.mock.calls.filter(([url]) => url === "/api/articles?limit=20&offset=0").length;
    resolveRun(response({ task_id: "t", status: "pending", run_id: "r" }));
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.filter(([url]) => url === "/api/articles?limit=20&offset=0").length,
      ).toBeGreaterThan(before),
    );
  });

  it("shows the feed request failure without rendering an empty state", async () => {
    stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ error: "Article index unavailable" }, 503);
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    expect(await screen.findByText("Article index unavailable")).toBeInTheDocument();
    expect(screen.queryByText("No articles found")).not.toBeInTheDocument();
  });

  it("opens the article drawer with its summary, metadata and fallback content", async () => {
    stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 1, articles: [{ ...article, source: null, category: null, content: null }] });
      if (url === "/api/summaries?article_id=a1&limit=20") return response({ count: 0, summaries: [] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    fireEvent.click(await screen.findByRole("button", { name: "Open article: Article One" }));
    expect(await screen.findByText("No summary available.")).toBeInTheDocument();
    const panel = within(screen.getByRole("dialog"));
    expect(panel.getByText(/Unknown source/)).toBeInTheDocument();
    expect(panel.getByText(/uncategorized/)).toBeInTheDocument();
    expect(panel.getByText("No extracted content available.")).toBeInTheDocument();
    expect(panel.getByRole("link", { name: "Open original article" })).toHaveAttribute(
      "href",
      article.url,
    );
  });

  it("loads and renders the related summary for a selected article", async () => {
    let resolveSummaries!: (value: MockResponse) => void;
    stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 1, articles: [article] });
      if (url === "/api/summaries?article_id=a1&limit=20") {
        return new Promise<MockResponse>((resolve) => { resolveSummaries = resolve; });
      }
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    fireEvent.click(await screen.findByRole("button", { name: "Open article: Article One" }));
    expect(await screen.findByText("Loading summary...")).toBeInTheDocument();
    resolveSummaries(
      response({
        count: 1,
        summaries: [{ id: "s1", article_id: "a1", summary_text: "## Summary\n\n- key point", model_used: "gpt", created_at: "2026-09-10T00:00:00Z" }],
      }),
    );
    expect(await screen.findByText("key point")).toBeInTheDocument();
  });

  it("reports a failed summary request for the selected article", async () => {
    stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 1, articles: [article] });
      if (url === "/api/summaries?article_id=a1&limit=20") return response({ error: "Summary store offline" }, 500);
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    fireEvent.click(await screen.findByRole("button", { name: "Open article: Article One" }));
    expect(await screen.findByText("Unable to load summary.")).toBeInTheDocument();
  });

  it("pages through a large result set and resets to the first page on a new search", async () => {
    const fetchMock = stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ digests: [] });
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 45, articles: [article] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    expect(await screen.findByText("Page 1 / 3")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "2" }));
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith("/api/articles?limit=20&offset=20", undefined),
    );
    expect(await screen.findByText("Page 2 / 3")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Search"), { target: { value: "fresh" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/articles?limit=20&offset=0&q=fresh",
        undefined,
      ),
    );
    expect(await screen.findByText("Page 1 / 3")).toBeInTheDocument();
  });

  it("opens the digest drawer, lists sibling digests and drills into a source article", async () => {
    let resolveDigestArticles!: (value: MockResponse) => void;
    stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") {
        return response({
          digests: [
            digest,
            { ...digest, id: "d0", title: "Earlier digest", created_at: "2026-09-01T00:00:00Z" },
            { ...digest, id: "d2", category: "world", title: "World digest" },
          ],
        });
      }
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 0, articles: [] });
      if (url === "/api/digests/d1/articles") {
        return new Promise<MockResponse>((resolve) => { resolveDigestArticles = resolve; });
      }
      if (url === "/api/summaries?article_id=a2&limit=20") return response({ count: 0, summaries: [] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    fireEvent.click(await screen.findByRole("button", { name: "Open digest: Latest digest" }));

    const panel = within(await screen.findByRole("dialog"));
    expect(await panel.findByText("Loading source articles...")).toBeInTheDocument();
    expect(panel.getByText("Status: success")).toBeInTheDocument();
    expect(panel.getByText("Model: gpt")).toBeInTheDocument();
    expect(panel.getByText("Digest body")).toBeInTheDocument();
    expect(panel.getByRole("button", { name: /Earlier digest · / })).toBeInTheDocument();

    resolveDigestArticles(response({ articles: [{ ...article, id: "a2", title: "Linked article" }] }));
    const linked = await panel.findByRole("button", { name: "Linked article" });
    fireEvent.click(linked);

    const articleLink = await screen.findByRole("link", { name: "Open original article" });
    expect(articleLink).toHaveAttribute("href", "https://example.com/one");
    expect(await screen.findByText("No summary available.")).toBeInTheDocument();
    expect(screen.getByText("Body text")).toBeInTheDocument();
  });

  it("reports digest failures, missing metadata and a failed source article request", async () => {
    stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") {
        return response({
          digests: [
            { ...digest, status: "failed", error: "LLM timeout", model_used: "", created_at: null, article_count: 1 },
          ],
        });
      }
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 0, articles: [] });
      if (url === "/api/digests/d1/articles") return response({ error: "Digest join failed" }, 500);
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    fireEvent.click(await screen.findByRole("button", { name: "Open digest: Latest digest" }));

    const panel = within(await screen.findByRole("dialog"));
    expect(await panel.findByText("Unable to load source articles.")).toBeInTheDocument();
    expect(panel.getByText("Status: failed")).toBeInTheDocument();
    expect(panel.getByText("LLM timeout")).toBeInTheDocument();
    expect(panel.getByText("Model: -")).toBeInTheDocument();
    expect(
      panel.getByText((_, node) => node?.tagName === "P" && node.textContent === "technology · 1 articles · -"),
    ).toBeInTheDocument();
  });

  it("surfaces a digest listing failure in the digest panel", async () => {
    stubApi((url) => {
      if (url === "/api/config") return response(config);
      if (url === "/api/digests") return response({ error: "Digest service down" }, 502);
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 0, articles: [] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    expect(await screen.findByText("Digest service down")).toBeInTheDocument();
  });

  it("keeps the feed usable when the config request fails", async () => {
    stubApi((url) => {
      if (url === "/api/config") return response({ error: "Config unavailable" }, 503);
      if (url === "/api/digests") return response({ digests: [] });
      if (url === "/api/runs") return response({ runs: [] });
      if (url === "/api/sources") return response({ sources: [] });
      if (url.startsWith("/api/articles?")) return response({ count: 0, articles: [] });
      return undefined;
    });
    renderWithProviders(<FeedPage />);
    await waitFor(() =>
      expect(screen.getByLabelText("Articles per update")).toHaveAttribute("placeholder", "20"),
    );
    expect(screen.getByRole("button", { name: "Search" })).toBeInTheDocument();
  });
});

describe("Settings route", () => {
  it("renders the settings page with the embedded configuration form", async () => {
    stubApi((url) => {
      if (url === "/api/config") return response({ ...config, llm_price_snapshot_json: "{}", schedule_times: "08:00", schedule_timezone: "Asia/Ho_Chi_Minh", retention_days: 30, telegram_enabled: false, telegram_configured: false, llm_configured: false });
      if (url === "/api/config/history?limit=20") return response({ history: [] });
      return undefined;
    });
    renderWithProviders(<SettingsPage />);
    expect(screen.getByRole("heading", { name: "Settings" })).toBeInTheDocument();
    expect(await screen.findByLabelText("Fetch limit")).toHaveValue("37");
  });
});
