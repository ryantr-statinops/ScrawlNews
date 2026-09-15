import { requestJson } from "../../lib/api";
import type { ArticleListResponse } from "../../types/api";

export function fetchArticles(params: Record<string, string> = {}): Promise<ArticleListResponse> {
  const q = new URLSearchParams(params).toString();
  return requestJson<ArticleListResponse>(`/api/articles?${q}`);
}
