export interface Article {
  id: string;
  title: string;
  url: string;
  source: string | null;
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
