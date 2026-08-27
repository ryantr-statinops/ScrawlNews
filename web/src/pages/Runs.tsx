import { useEffect, useState } from "react";
import { fetchRuns, triggerRun } from "../lib/api";

export default function Runs() {
  const [runs, setRuns] = useState<{ runs: unknown[] }>({ runs: [] });

  useEffect(() => {
    fetchRuns().then(setRuns);
  }, []);

  const onRun = async () => {
    const res = await triggerRun(20);
    alert(`Triggered ${res.task_id}`);
    fetchRuns().then(setRuns);
  };

  return (
    <div>
      <h2>Runs</h2>
      <button onClick={onRun}>Run Now</button>
      <ul>
        {runs.runs.map((r: unknown, i: number) => (
          <li key={i}>{JSON.stringify(r)}</li>
        ))}
      </ul>
    </div>
  );
}
