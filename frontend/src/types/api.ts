export interface Article {
  id: string;
  title: string;
  url: string;
  source: string | null;
  category?: string | null;
  content?: string | null;
  fetched_at: string | null;
  published_at?: string | null;
  summarized: number;
}

export interface Digest {
  id: string;
  category: string;
  title: string;
  digest_text: string;
  article_count: number;
  model_used: string;
  status: string;
  error: string | null;
  created_at: string | null;
}

export interface Summary {
  id: string;
  article_id: string;
  summary_text: string;
  model_used: string;
  created_at: string | null;
}

export interface PipelineRun {
  id: string;
  status: "pending" | "running" | "success" | "failed";
  task_id: string | null;
  articles_fetched: number;
  summaries_generated: number;
  telegram_sent: number;
  error: string | null;
  started_at: string;
  finished_at: string | null;
}

export interface AgentDecision {
  status: string;
  reason: string;
  action: { kind: string; dry_run: boolean } | null;
  correlation_id: string;
}

export interface AgentVerification {
  status: string;
  message: string;
  correlation_id: string;
}

export interface AgentRunResponse {
  decision: AgentDecision;
  verification: AgentVerification;
}

export interface AgentAuditEvent {
  id: number;
  correlation_id: string;
  phase: string;
  status: string;
  message: string;
  created_at: string;
}

export interface ArticleListResponse {
  count: number;
  articles: Article[];
}

export interface DigestListResponse {
  digests: Digest[];
}

export interface SummaryListResponse {
  count: number;
  summaries: Summary[];
}

export interface DigestArticlesResponse {
  articles: Article[];
}

export interface RunListResponse {
  runs: PipelineRun[];
}

export interface ConfigResponse {
  fetch_limit: number;
  summary_lang: string;
  llm_provider: string;
  llm_model: string;
  llm_configured: boolean;
  telegram_enabled: boolean;
  telegram_configured: boolean;
  retention_days: number;
  news_categories: string;
  schedule_times: string;
  schedule_timezone: string;
  news_country: string;
  news_city: string;
  log_level: string;
}

export interface ConfigUpdateResponse {
  updated: Record<string, string>;
}

export interface Source {
  id: string;
  name: string;
  url: string;
  category: string | null;
  enabled: number;
}

export interface SourceListResponse {
  sources: Source[];
}

export interface ConfigHistoryResponse {
  history: Array<{
    key: string;
    old_value: string | null;
    new_value: string;
    changed_at: string;
  }>;
}

export interface HealthResponse {
  status: string;
  db: string;
  redis: string;
}
