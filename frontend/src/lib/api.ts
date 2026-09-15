import type {
  ArticleListResponse,
  ConfigHistoryResponse,
  ConfigResponse,
  ConfigUpdateResponse,
  DigestArticlesResponse,
  DigestListResponse,
  RunListResponse,
  Source,
  SourceListResponse,
  SummaryListResponse,
} from "../types/api";

export class ApiError extends Error {
  constructor(message: string, readonly status: number, readonly body?: unknown) {
    super(message);
    this.name = "ApiError";
  }
}

function errorMessage(body: unknown, status: number): string {
  if (typeof body === "object" && body !== null) {
    const payload = body as { error?: unknown; detail?: unknown };
    if (typeof payload.error === "string") return payload.error;
    if (typeof payload.detail === "string") return payload.detail;
  }
  return `Request failed: ${status}`;
}

export async function requestJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  const text = await response.text();
  let body: unknown;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      throw new ApiError("Server returned invalid JSON", response.status);
    }
  }
  if (!response.ok) throw new ApiError(errorMessage(body, response.status), response.status, body);
  return body as T;
}

export function fetchArticles(params: Record<string, string> = {}): Promise<ArticleListResponse> {
  const q = new URLSearchParams(params).toString();
  return requestJson<ArticleListResponse>(`/api/articles?${q}`);
}

export function fetchRuns(): Promise<RunListResponse> {
  return requestJson<RunListResponse>("/api/runs");
}

export function triggerRun(fetch_limit?: number, categories?: string[]) {
  const params = new URLSearchParams();
  if (fetch_limit !== undefined) params.set("fetch_limit", String(fetch_limit));
  if (categories?.length) params.set("categories", categories.join(","));
  const query = params.toString();
  return requestJson<{ task_id: string; status: string; run_id: string }>(
    `/api/runs${query ? `?${query}` : ""}`,
    { method: "POST" },
  );
}

export function fetchConfig(): Promise<ConfigResponse> {
  return requestJson<ConfigResponse>("/api/config");
}

export function fetchConfigHistory(): Promise<ConfigHistoryResponse> {
  return requestJson<ConfigHistoryResponse>("/api/config/history?limit=20");
}

export function fetchDigests(category?: string): Promise<DigestListResponse> {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  return requestJson<DigestListResponse>(`/api/digests${query}`);
}

export function fetchSummaries(articleId: string): Promise<SummaryListResponse> {
  return requestJson<SummaryListResponse>(
    `/api/summaries?article_id=${encodeURIComponent(articleId)}&limit=20`,
  );
}

export function fetchDigestArticles(digestId: string): Promise<DigestArticlesResponse> {
  return requestJson<DigestArticlesResponse>(`/api/digests/${encodeURIComponent(digestId)}/articles`);
}

export function updateConfig(payload: Record<string, unknown>): Promise<ConfigUpdateResponse> {
  return requestJson<ConfigUpdateResponse>("/api/config", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchSources(query = ""): Promise<SourceListResponse> {
  return requestJson<SourceListResponse>(
    `/api/sources${query ? `?q=${encodeURIComponent(query)}` : ""}`,
  );
}

export function updateSource(id: string, payload: Record<string, unknown>): Promise<Source> {
  return requestJson<Source>(`/api/sources/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function createSource(payload: Record<string, unknown>): Promise<Source> {
  return requestJson<Source>("/api/sources", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
