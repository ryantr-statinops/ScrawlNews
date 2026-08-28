import { useEffect, useState } from "react";

export default function Summaries() {
  const [data, setData] = useState<{ count: number; summaries: unknown[] }>({ count: 0, summaries: [] });

  useEffect(() => {
    fetch("/api/summaries")
      .then((r) => r.json())
      .then(setData);
  }, []);

  return (
    <div>
      <h2>Summaries</h2>
      <p>Count: {data.count}</p>
      <ul>
        {data.summaries.map((s: unknown, i: number) => (
          <li key={i}>{JSON.stringify(s)}</li>
        ))}
      </ul>
    </div>
  );
}
