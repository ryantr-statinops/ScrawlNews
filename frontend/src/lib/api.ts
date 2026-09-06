export async function fetchArticles(params: Record<string, string> = {}) {
  const q = new URLSearchParams(params).toString();
  const res = await fetch(`/api/articles?${q}`);
  return res.json();
}

export async function fetchRuns() {
  const res = await fetch("/api/runs");
  return res.json();
}

export async function triggerRun(fetch_limit?: number) {
  const res = await fetch("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fetch_limit }),
  });
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
