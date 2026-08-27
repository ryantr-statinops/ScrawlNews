import { useEffect, useState } from "react";
import { fetchConfig, updateConfig } from "../lib/api";

export default function Config() {
  const [cfg, setCfg] = useState<Record<string, unknown>>({});

  useEffect(() => {
    fetchConfig().then(setCfg);
  }, []);

  const onSave = async () => {
    const res = await updateConfig({ fetch_limit: cfg.fetch_limit });
    alert(JSON.stringify(res));
  };

  return (
    <div>
      <h2>Config</h2>
      <pre>{JSON.stringify(cfg, null, 2)}</pre>
      <button onClick={onSave}>Save</button>
    </div>
  );
}
