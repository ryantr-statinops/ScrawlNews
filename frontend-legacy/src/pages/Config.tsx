import { useEffect, useState } from "react";
import { fetchConfig, updateConfig, ConfigResponse } from "../lib/api";

export default function Config() {
  const [cfg, setCfg] = useState<ConfigResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchConfig().then(setCfg);
  }, []);

  const onSave = async () => {
    if (!cfg) return;
    setSaving(true);
    setMessage(null);
    try {
      const res = await updateConfig({
        fetch_limit: cfg.fetch_limit,
        summary_lang: cfg.summary_lang,
        telegram_enabled: cfg.telegram_enabled,
        retention_days: cfg.retention_days,
      });
      setMessage(`Saved: ${JSON.stringify(res.updated)}`);
    } catch {
      setMessage("Save failed");
    } finally {
      setSaving(false);
    }
  };

  if (!cfg) return <div>Loading...</div>;

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Config</h2>
      <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 16, maxWidth: 480, display: "flex", flexDirection: "column", gap: 12 }}>
        <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Fetch Limit</span>
          <input type="number" value={cfg.fetch_limit} onChange={(e) => setCfg({ ...cfg, fetch_limit: Number(e.target.value) })} style={{ width: 100, padding: 6, border: "1px solid #cbd5e1", borderRadius: 4 }} />
        </label>
        <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Summary Lang</span>
          <select value={cfg.summary_lang} onChange={(e) => setCfg({ ...cfg, summary_lang: e.target.value })} style={{ width: 100, padding: 6, border: "1px solid #cbd5e1", borderRadius: 4 }}>
            <option value="vi">vi</option>
            <option value="en">en</option>
          </select>
        </label>
        <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Telegram Enabled</span>
          <input type="checkbox" checked={cfg.telegram_enabled} onChange={(e) => setCfg({ ...cfg, telegram_enabled: e.target.checked })} />
        </label>
        <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Retention Days</span>
          <input type="number" value={cfg.retention_days} onChange={(e) => setCfg({ ...cfg, retention_days: Number(e.target.value) })} style={{ width: 100, padding: 6, border: "1px solid #cbd5e1", borderRadius: 4 }} />
        </label>

        <button onClick={onSave} disabled={saving} style={{ padding: "8px 16px", background: "#0f172a", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
          {saving ? "Saving..." : "Save"}
        </button>
        {message && <p style={{ margin: 0, color: "#166534", fontSize: 14 }}>{message}</p>}
      </div>
    </div>
  );
}
