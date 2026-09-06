import { useEffect, useState } from "react";
import { fetchSummaries, Summary } from "../lib/api";

export default function Summaries() {
  const [data, setData] = useState<{ count: number; summaries: Summary[] }>({ count: 0, summaries: [] });
  const [selected, setSelected] = useState<Summary | null>(null);

  useEffect(() => {
    fetchSummaries().then(setData);
  }, []);

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Summaries</h2>
      <p style={{ color: "#475569" }}>Total: {data.count}</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 12 }}>
        {data.summaries.map((s) => (
          <div key={s.id} onClick={() => setSelected(s)} style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 14, cursor: "pointer" }}>
            <div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>{s.model_used}</div>
            <div style={{ fontSize: 14, lineHeight: 1.4 }}>{s.summary_text}</div>
            <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 8 }}>{new Date(s.created_at ?? "").toLocaleString()}</div>
          </div>
        ))}
      </div>

      {selected && (
        <div onClick={() => setSelected(null)} style={{ position: "fixed", inset: 0, background: "rgba(15,23,42,0.4)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 50 }}>
          <div onClick={(e) => e.stopPropagation()} style={{ background: "#fff", borderRadius: 8, padding: 20, maxWidth: 560, width: "90%" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>Summary Detail</h3>
              <button onClick={() => setSelected(null)} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 16 }}>✕</button>
            </div>
            <div style={{ fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{selected.summary_text}</div>
            <div style={{ marginTop: 12, fontSize: 12, color: "#64748b" }}>Model: {selected.model_used} · Article: {selected.article_id}</div>
          </div>
        </div>
      )}
    </div>
  );
}
