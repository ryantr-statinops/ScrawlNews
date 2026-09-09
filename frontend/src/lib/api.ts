export async function fetchArticles(params: Record<string, string> = {}) {
  const q = new URLSearchParams(params).toString();
  const res = await fetch(`/api/articles?${q}`);
  return res.json();
}

export async function fetchRuns() {
  const res = await fetch("/api/runs");
  return res.json();
}

export async function triggerRun(fetch_limit?: number, categories?: string[]) {
  const params = new URLSearchParams();
  if (fetch_limit !== undefined) params.set("fetch_limit", String(fetch_limit));
  if (categories?.length) params.set("categories", categories.join(","));
  const query = params.toString();
  const res = await fetch(`/api/runs${query ? `?${query}` : ""}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed to trigger run: ${res.status}`);
  return res.json();
}

export async function fetchConfig() {
  const res = await fetch("/api/config");
  return res.json();
}

export async function updateConfig(payload: Record<string, unknown>) {
  const res = await fetch("/api/config", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}
