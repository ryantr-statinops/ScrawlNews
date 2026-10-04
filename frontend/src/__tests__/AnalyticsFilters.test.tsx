import { afterEach, describe, expect, it } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { useAnalyticsFilters } from "../features/analytics/useAnalyticsFilters";

afterEach(() => {
  window.history.replaceState(null, "", "/analytics");
});

describe("analytics filter URL state", () => {
  it("restores a supported tab, window and encoded filters from the URL", () => {
    window.history.replaceState(
      null,
      "",
      "/analytics?tab=ai-usage&window=7d&category=World+News&source_id=Daily%2FVN&provider=azure%2Fopenai&model=gpt%2B4",
    );
    const { result } = renderHook(() => useAnalyticsFilters());
    expect(result.current.tab).toBe("ai-usage");
    expect(result.current.filters).toEqual({
      window: "7d",
      category: "World News",
      sourceId: "Daily/VN",
      provider: "azure/openai",
      model: "gpt+4",
    });
  });

  it("falls back to defaults for unsupported tab and window values", () => {
    window.history.replaceState(null, "", "/analytics?tab=legacy-pipeline&window=90d");
    const { result } = renderHook(() => useAnalyticsFilters());
    expect(result.current.tab).toBe("overview");
    expect(result.current.filters).toEqual({
      window: "24h",
      category: null,
      sourceId: null,
      provider: null,
      model: null,
    });
  });

  it("serializes only the active filters into the URL with form encoding", () => {
    window.history.replaceState(null, "", "/analytics?tab=content&window=1h&category=science&provider=openai");
    const { result } = renderHook(() => useAnalyticsFilters());

    act(() => result.current.setTab("sources"));
    let search = window.location.search;
    expect(search).toBe("?tab=sources&window=1h&category=science&provider=openai");
    expect(new URLSearchParams(search).has("model")).toBe(false);

    act(() => result.current.setFilters({ window: "30d", category: "World News", sourceId: "Daily/VN", provider: null, model: "gpt+4" }));
    search = window.location.search;
    expect(search).toBe("?tab=sources&window=30d&category=World+News&source_id=Daily%2FVN&model=gpt%2B4");
    expect(new URLSearchParams(search).has("provider")).toBe(false);
    expect(new URLSearchParams(search).get("source_id")).toBe("Daily/VN");
    expect(new URLSearchParams(search).get("model")).toBe("gpt+4");
  });

  it("writes the default tab and window when the URL carries no query", () => {
    window.history.replaceState(null, "", "/analytics");
    const { result } = renderHook(() => useAnalyticsFilters());
    expect(result.current.tab).toBe("overview");
    expect(result.current.filters.window).toBe("24h");
    expect(window.location.search).toBe("?tab=overview&window=24h");
  });
});
