import { useEffect, useState } from "react";
import { fetchHealth } from "../lib/api";

type Health = { status: string; db: string; redis: string };

export default function Health() {
  const [health, setHealth] = useState<Health | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    fetchHealth().then(setHealth);
    const es = new EventSource("/api/logs/stream");
    es.onmessage = (e) => setLogs((prev) => [...prev, e.data].slice(-50));
    es.onerror = () => es.close();
    return () => es.close();
  }, []);

  const statusColor = (s: string) => (s === "ok" ? "#dcfce7" : "#fee2e2");
  const statusText = (s: string) => (s === "ok" ? "#166534" : "#991b1b");

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>System Health</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 20 }}>
        {health && ["status", "db", "redis"].map((key) => (
          <div key={key} style={{ background: statusColor(health[key]), color: statusText(health[key]), padding: 16, borderRadius: 8, textTransform: "capitalize" }}>
            <div style={{ fontSize: 12, opacity: 0.8 }}>{key}</div>
            <div style={{ fontSize: 18, fontWeight: 600 }}>{health[key]}</div>
          </div>
        ))}
      </div>

      <h3>Logs SSE</h3>
      <div style={{ background: "#0f172a", color: "#e2e8f0", padding: 12, borderRadius: 8, fontFamily: "monospace", fontSize: 12, maxHeight: 300, overflowY: "auto" }}>
        {logs.length === 0 && <div style={{ color: "#64748b" }}>Waiting for logs...</div>}
        {logs.map((l, i) => <div key={i}>{l}</div>)}
      </div>
    </div>
  );
}
