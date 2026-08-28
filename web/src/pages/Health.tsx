import { useEffect, useState } from "react";

export default function Health() {
  const [health, setHealth] = useState<{ status: string; db: string; redis: string } | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    fetch("/health")
      .then((r) => r.json())
      .then(setHealth);
    const es = new EventSource("/api/logs/stream");
    es.onmessage = (e) => setLogs((prev) => [...prev, e.data].slice(-20));
    return () => es.close();
  }, []);

  return (
    <div>
      <h2>System Health</h2>
      <pre>{JSON.stringify(health, null, 2)}</pre>
      <h3>Logs SSE</h3>
      <ul>
        {logs.map((l, i) => (
          <li key={i}>{l}</li>
        ))}
      </ul>
    </div>
  );
}
