import { useEffect, useState, useCallback } from "react";
import { fetchRuns, triggerRun, PipelineRun } from "../lib/api";

export default function Runs() {
  const [runs, setRuns] = useState<{ runs: PipelineRun[] }>({ runs: [] });
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    const res = await fetchRuns();
    setRuns(res);
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [load]);

  const onRun = async (fetch_limit = 20) => {
    setLoading(true);
    try {
      await triggerRun(fetch_limit);
      setTimeout(load, 1000);
    } finally {
      setLoading(false);
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "success": return "#dcfce7";
      case "failed": return "#fee2e2";
      case "running": return "#e0f2fe";
      default: return "#fef9c3";
    }
  };

  const statusTextColor = (status: string) => {
    switch (status) {
      case "success": return "#166534";
      case "failed": return "#991b1b";
      case "running": return "#075985";
      default: return "#854d0e";
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Runs</h2>
        <button onClick={() => onRun(20)} disabled={loading} style={{ padding: "8px 16px", background: "#0f172a", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
          {loading ? "Running..." : "Run Now"}
        </button>
      </div>

      <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead style={{ background: "#f1f5f9" }}>
            <tr>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>ID</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Status</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Articles</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Summaries</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Telegram</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Started</th>
            </tr>
          </thead>
          <tbody>
            {runs.runs.length === 0 && (
              <tr><td colSpan={6} style={{ padding: 20, textAlign: "center", color: "#64748b" }}>No runs yet</td></tr>
            )}
            {runs.runs.map((r) => (
              <tr key={r.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                <td style={{ padding: 10, fontFamily: "monospace", fontSize: 12 }}>{r.id.slice(0, 8)}</td>
                <td style={{ padding: 10 }}>
                  <span style={{ padding: "2px 8px", borderRadius: 12, fontSize: 12, background: statusColor(r.status), color: statusTextColor(r.status), textTransform: "capitalize" }}>
                    {r.status}
                  </span>
                </td>
                <td style={{ padding: 10 }}>{r.articles_fetched ?? 0}</td>
                <td style={{ padding: 10 }}>{r.summaries_generated ?? 0}</td>
                <td style={{ padding: 10 }}>{r.telegram_sent ? "Yes" : "No"}</td>
                <td style={{ padding: 10, color: "#475569" }}>{r.started_at ? new Date(r.started_at).toLocaleString() : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
