import { useEffect, useState } from "react";
import { fetchRuns, PipelineRun } from "../lib/api";

export default function Delivery() {
  const [runs, setRuns] = useState<{ runs: PipelineRun[] }>({ runs: [] });

  useEffect(() => {
    fetchRuns().then(setRuns);
  }, []);

  const telegramRuns = runs.runs.filter((r) => r.telegram_sent === 1);
  const failedRuns = runs.runs.filter((r) => r.status === "failed");

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Delivery Monitor</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12, marginBottom: 20 }}>
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
          <div style={{ fontSize: 12, color: "#64748b" }}>Total Runs</div>
          <div style={{ fontSize: 24, fontWeight: 600 }}>{runs.runs.length}</div>
        </div>
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
          <div style={{ fontSize: 12, color: "#64748b" }}>Telegram Sent</div>
          <div style={{ fontSize: 24, fontWeight: 600, color: "#166534" }}>{telegramRuns.length}</div>
        </div>
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 16 }}>
          <div style={{ fontSize: 12, color: "#64748b" }}>Failed</div>
          <div style={{ fontSize: 24, fontWeight: 600, color: "#991b1b" }}>{failedRuns.length}</div>
        </div>
      </div>

      <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead style={{ background: "#f1f5f9" }}>
            <tr>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Run ID</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Status</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Telegram</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Started</th>
            </tr>
          </thead>
          <tbody>
            {runs.runs.length === 0 && (
              <tr><td colSpan={4} style={{ padding: 20, textAlign: "center", color: "#64748b" }}>No delivery history</td></tr>
            )}
            {runs.runs.map((r) => (
              <tr key={r.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                <td style={{ padding: 10, fontFamily: "monospace", fontSize: 12 }}>{r.id.slice(0, 8)}</td>
                <td style={{ padding: 10, textTransform: "capitalize" }}>{r.status}</td>
                <td style={{ padding: 10 }}>{r.telegram_sent ? "Sent" : "Not sent"}</td>
                <td style={{ padding: 10, color: "#475569" }}>{r.started_at ? new Date(r.started_at).toLocaleString() : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
