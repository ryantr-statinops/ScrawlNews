import { useEffect, useState } from "react";
import type { AnalyticsFiltersState, AnalyticsTab, AnalyticsWindow } from "./types";

const windows: AnalyticsWindow[] = ["1h", "4h", "12h", "24h", "7d", "30d"];
const tabs: AnalyticsTab[] = ["overview", "content", "pipeline", "sources", "ai-usage"];

function initialState() {
  const params = new URLSearchParams(window.location.search);
  const requestedWindow = params.get("window") as AnalyticsWindow | null;
  const requestedTab = params.get("tab") as AnalyticsTab | null;
  return {
    filters: {
      window: windows.includes(requestedWindow ?? "24h") ? requestedWindow ?? "24h" : "24h",
      category: params.get("category"),
      sourceId: params.get("source_id"),
      provider: params.get("provider"),
      model: params.get("model"),
    } satisfies AnalyticsFiltersState,
    tab: tabs.includes(requestedTab ?? "overview") ? requestedTab ?? "overview" : "overview",
  };
}

export function useAnalyticsFilters() {
  const initial = initialState();
  const [filters, setFilters] = useState<AnalyticsFiltersState>(initial.filters);
  const [tab, setTab] = useState<AnalyticsTab>(initial.tab);

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tab", tab);
    params.set("window", filters.window);
    if (filters.category) params.set("category", filters.category);
    if (filters.sourceId) params.set("source_id", filters.sourceId);
    if (filters.provider) params.set("provider", filters.provider);
    if (filters.model) params.set("model", filters.model);
    window.history.replaceState(null, "", `${window.location.pathname}?${params}`);
  }, [filters, tab]);

  return { filters, setFilters, tab, setTab };
}
