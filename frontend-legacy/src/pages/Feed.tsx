import { useEffect, useState, useMemo } from "react";
import { fetchArticles, Article } from "../lib/api";

export default function Feed() {
  const [data, setData] = useState<{ count: number; articles: Article[] }>({ count: 0, articles: [] });
  const [q, setQ] = useState("");
  const [source, setSource] = useState("");
  const [limit, setLimit] = useState(20);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { limit, offset };
      if (q) params.q = q;
      if (source) params.source = source;
      const res = await fetchArticles(params);
      setData({ count: res.count, articles: res.articles ?? [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [limit, offset]);

  const sources = useMemo(() => Array.from(new Set(data.articles.map((a) => a.source).filter(Boolean))) as string[], [data.articles]);
  const totalPages = Math.max(1, Math.ceil(data.count / limit));
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Feed</h2>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input placeholder="Search..." value={q} onChange={(e) => setQ(e.target.value)} style={{ padding: 6, border: "1px solid #cbd5e1", borderRadius: 4 }} />
          <select value={source} onChange={(e) => setSource(e.target.value)} style={{ padding: 6, border: "1px solid #cbd5e1", borderRadius: 4 }}>
            <option value="">All sources</option>
            {sources.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <button onClick={() => { setOffset(0); load(); }} disabled={loading} style={{ padding: "6px 12px", background: "#0f172a", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            {loading ? "Loading..." : "Search"}
          </button>
        </div>
      </div>

      <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead style={{ background: "#f1f5f9" }}>
            <tr>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Title</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Source</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Fetched</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.articles.length === 0 && (
              <tr><td colSpan={4} style={{ padding: 20, textAlign: "center", color: "#64748b" }}>No articles found</td></tr>
            )}
            {data.articles.map((a) => (
              <tr key={a.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                <td style={{ padding: 10, maxWidth: 400, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  <a href={a.url} target="_blank" rel="noreferrer" style={{ color: "#0f172a", textDecoration: "none" }}>{a.title}</a>
                </td>
                <td style={{ padding: 10, color: "#475569" }}>{a.source || "-"}</td>
                <td style={{ padding: 10, color: "#475569" }}>{a.fetched_at ? new Date(a.fetched_at).toLocaleString() : "-"}</td>
                <td style={{ padding: 10 }}>
                  <span style={{ padding: "2px 8px", borderRadius: 12, fontSize: 12, background: a.summarized ? "#dcfce7" : "#fef9c3", color: a.summarized ? "#166534" : "#854d0e" }}>
                    {a.summarized ? "Summarized" : "Pending"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 12 }}>
        <span style={{ color: "#475569", fontSize: 14 }}>Total: {data.count} · Page {currentPage} / {totalPages}</span>
        <div style={{ display: "flex", gap: 8 }}>
          <button disabled={currentPage <= 1 || loading} onClick={() => setOffset(Math.max(0, offset - limit))} style={{ padding: "6px 12px", border: "1px solid #cbd5e1", borderRadius: 4, background: "#fff", cursor: "pointer" }}>Prev</button>
          <button disabled={currentPage >= totalPages || loading} onClick={() => setOffset(offset + limit)} style={{ padding: "6px 12px", border: "1px solid #cbd5e1", borderRadius: 4, background: "#fff", cursor: "pointer" }}>Next</button>
        </div>
      </div>
    </div>
  );
}
