import { useEffect, useState } from "react";

export default function Analytics() {
  const [stats, setStats] = useState<{ articles_per_day: unknown[]; source_dist: unknown[] } | null>(null);

  useEffect(() => {
    fetch("/api/stats")
      .then((r) => r.json())
      .then(setStats);
  }, []);

  return (
    <div>
      <h2>Analytics</h2>
      <pre>{JSON.stringify(stats, null, 2)}</pre>
    </div>
  );
}
