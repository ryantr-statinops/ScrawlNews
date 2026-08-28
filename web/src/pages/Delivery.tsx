import { useEffect, useState } from "react";

export default function Delivery() {
  const [runs, setRuns] = useState<{ runs: { id: string; telegram_sent: number }[] }>({ runs: [] });

  useEffect(() => {
    fetch("/api/runs")
      .then((r) => r.json())
      .then(setRuns);
  }, []);

  return (
    <div>
      <h2>Delivery Monitor</h2>
      <p>Telegram preview split 4096, fallback file</p>
      <ul>
        {runs.runs.map((r) => (
          <li key={r.id}>
            {r.id}: sent={r.telegram_sent}
          </li>
        ))}
      </ul>
    </div>
  );
}
