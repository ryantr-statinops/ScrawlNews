export interface Article {
  id: string;
  url: string;
  title: string;
  source?: string;
  content?: string;
  fetched_at?: string;
  summarized?: number;
}

export interface Summary {
  id: string;
  article_id: string;
  summary_text: string;
  model_used: string;
  created_at?: string;
}

export interface PipelineRun {
  id: string;
  status: string;
  task_id?: string;
  articles_fetched?: number;
  summaries_generated?: number;
  telegram_sent?: number;
  error?: string;
  started_at?: string;
  finished_at?: string;
}

export interface ConfigResponse {
  fetch_limit: number;
  summary_lang: string;
  llm_provider: string;
  llm_model: string;
  telegram_enabled: boolean;
  retention_days: number;
  log_level: string;
}

export interface PaginatedResponse<T> {
  count: number;
  articles?: T[];
}

export async function fetchArticles(params: Record<string, string | number> = {}): Promise<PaginatedResponse<Article>> {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => q.set(k, String(v)));
  const res = await fetch(`/api/articles?${q.toString()}`);
  return res.json();
}

export async function fetchSummaries(params: Record<string, string | number> = {}): Promise<PaginatedResponse<Summary>> {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => q.set(k, String(v)));
  const res = await fetch(`/api/summaries?${q.toString()}`);
  return res.json();
}

export async function fetchRuns(): Promise<{ runs: PipelineRun[] }> {
  const res = await fetch("/api/runs");
  return res.json();
}

export async function triggerRun(fetch_limit?: number): Promise<{ task_id: string; status: string; run_id: string }> {
  const res = await fetch("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fetch_limit }),
  });
  return res.json();
}

export async function fetchConfig(): Promise<ConfigResponse> {
  const res = await fetch("/api/config");
  return res.json();
}

export async function updateConfig(payload: Record<string, unknown>): Promise<{ updated: Record<string, unknown> }> {
  const res = await fetch("/api/config", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function fetchStats(): Promise<{
  articles_per_day: { day: string; count: number }[];
  summaries_per_day: { day: string; count: number }[];
  source_dist: { source: string; count: number }[];
  cost_estimate: number;
}> {
  const res = await fetch("/api/stats");
  return res.json();
}

export async function fetchHealth(): Promise<{ status: string; db: string; redis: string }> {
  const res = await fetch("/health");
  return res.json();
}
