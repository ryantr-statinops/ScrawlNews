import type { Article } from "../../types/api";

interface FeedResponse {
  count: number;
  articles: Article[];
}

export async function fetchArticles(params: Record<string, string> = {}): Promise<FeedResponse> {
  const q = new URLSearchParams(params).toString();
  const res = await fetch(`/api/articles?${q}`);
  if (!res.ok) throw new Error(`Failed to fetch articles: ${res.status}`);
  return res.json();
}
