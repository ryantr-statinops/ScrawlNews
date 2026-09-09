export type AnalyticsWindow = "1h" | "4h" | "12h" | "24h" | "7d" | "30d";
export type AnalyticsTab = "overview" | "content" | "pipeline" | "sources" | "ai-usage";

export interface AnalyticsFiltersState {
  window: AnalyticsWindow;
  category: string | null;
  sourceId: string | null;
  provider: string | null;
  model: string | null;
}

export interface ComparisonMetric {
  current: number;
  previous: number;
  delta: number;
  delta_percent: number | null;
}

export interface AnalyticsPeriod {
  window: AnalyticsWindow;
  timezone: string;
  current: { from: string; to: string };
  previous: { from: string; to: string };
}

export interface BreakdownRow {
  current: number;
  previous: number;
  delta: number;
  delta_percent: number | null;
  [key: string]: string | number | null;
}

export interface OverviewResponse {
  period: AnalyticsPeriod;
  kpis: Record<string, ComparisonMetric>;
  alerts: Array<{ severity: "warning" | "error"; kind: string; count: number }>;
  trend: Array<{ timestamp: string; articles: number; summaries: number }>;
  categories: BreakdownRow[];
  sources: BreakdownRow[];
}

export interface ContentResponse {
  period: AnalyticsPeriod;
  velocity: Array<{ timestamp: string; articles: number; summaries: number }>;
  categories: BreakdownRow[];
  sources: BreakdownRow[];
  diversity: number;
  freshness: Record<string, number>;
}

export interface PipelineResponse {
  period: AnalyticsPeriod;
  kpis: Record<string, ComparisonMetric>;
  stages: Array<{
    stage: string;
    calls: number;
    median_seconds: number;
    p95_seconds: number;
    items: number;
    failures: number;
  }>;
  errors: Array<{ stage: string; error_class: string; count: number }>;
  runs: Array<Record<string, string | number | null>>;
}

export interface SourceAnalyticsResponse {
  period: AnalyticsPeriod;
  sources: Array<{
    source_id: string;
    source_name: string;
    category: string | null;
    country: string | null;
    fetches: number;
    success_rate: number;
    fetched: number;
    new: number;
    duplicates: number;
    duplicate_rate: number;
    median_latency_ms: number;
    p95_latency_ms: number;
    last_success_at: string | null;
    last_error: string | null;
  }>;
}

export interface AiUsageResponse {
  period: AnalyticsPeriod;
  kpis: Record<string, ComparisonMetric>;
  trend: Array<{ timestamp: string; input_tokens: number; output_tokens: number; requests: number }>;
  providers: Array<Record<string, string | number>>;
  models: Array<Record<string, string | number>>;
  operations: Array<Record<string, string | number>>;
}

export interface DrilldownResponse {
  period: AnalyticsPeriod;
  kind: string;
  records: Array<Record<string, string | number | null>>;
}
