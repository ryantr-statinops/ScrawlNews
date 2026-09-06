import { useEffect, useState } from "react";

export function useLogStream() {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const es = new EventSource("/api/logs/stream");
    es.onmessage = (e) => setLogs((prev) => [...prev, e.data].slice(-50));
    return () => es.close();
  }, []);

  return logs;
}
