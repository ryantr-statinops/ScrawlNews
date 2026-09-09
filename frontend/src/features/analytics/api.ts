import type {
  AiUsageResponse,
  AnalyticsFiltersState,
  ContentResponse,
  DrilldownResponse,
  OverviewResponse,
  PipelineResponse,
  SourceAnalyticsResponse,
} from "./types";

function query(filters: AnalyticsFiltersState, extra: Record<string, string> = {}) {
  const params = new URLSearchParams({ window: filters.window, ...extra });
  if (filters.category) params.set("category", filters.category);
  if (filters.sourceId) params.set("source_id", filters.sourceId);
  if (filters.provider) params.set("provider", filters.provider);
  if (filters.model) params.set("model", filters.model);
  return params.toString();
}

async function get<T>(path: string, filters: AnalyticsFiltersState, extra?: Record<string, string>) {
  const response = await fetch(`${path}?${query(filters, extra)}`);
  if (!response.ok) throw new Error(`Analytics request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export const analyticsApi = {
  overview: (filters: AnalyticsFiltersState) => get<OverviewResponse>("/api/analytics/overview", filters),
  content: (filters: AnalyticsFiltersState) => get<ContentResponse>("/api/analytics/content", filters),
  pipeline: (filters: AnalyticsFiltersState) => get<PipelineResponse>("/api/analytics/pipeline", filters),
  sources: (filters: AnalyticsFiltersState) => get<SourceAnalyticsResponse>("/api/analytics/sources", filters),
  aiUsage: (filters: AnalyticsFiltersState) => get<AiUsageResponse>("/api/analytics/ai-usage", filters),
  drilldown: (filters: AnalyticsFiltersState, extra: Record<string, string>) =>
    get<DrilldownResponse>("/api/analytics/drilldown", filters, extra),
};
