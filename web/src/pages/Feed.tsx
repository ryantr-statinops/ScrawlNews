import { useEffect, useState } from "react";
import { fetchArticles } from "../lib/api";

export default function Feed() {
  const [data, setData] = useState<{ count: number; articles: unknown[] }>({ count: 0, articles: [] });

  useEffect(() => {
    fetchArticles().then(setData);
  }, []);

  return (
    <div>
      <h2>Feed</h2>
      <p>Count: {data.count}</p>
      <ul>
        {data.articles.map((a: unknown, i: number) => (
          <li key={i}>{JSON.stringify(a)}</li>
        ))}
      </ul>
    </div>
  );
}
