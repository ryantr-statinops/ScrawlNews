import type { ReactNode } from "react";
import "./FeedWorkspace.css";

export function FeedWorkspace({ articles, digests, agent }: { articles: ReactNode; digests: ReactNode; agent: ReactNode }) {
  return <div className="feed-workspace">
    <section aria-label="Feed tools">{agent}{digests}</section>
    <section aria-label="Articles">{articles}</section>
  </div>;
}
