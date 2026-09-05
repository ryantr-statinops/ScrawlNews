export interface Article {
  id: string;
  title: string;
  url: string;
  source: string | null;
  fetched_at: string | null;
  summarized: number;
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
