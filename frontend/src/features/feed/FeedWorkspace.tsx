import type { ReactNode } from "react";
import { Stack } from "@mantine/core";
import "./FeedWorkspace.css";

export function FeedWorkspace({ articles, digests, agent }: { articles: ReactNode; digests: ReactNode; agent: ReactNode }) {
  return <div className="feed-workspace">
    <section className="feed-workspace__utility" aria-label="Feed tools">
      <Stack className="feed-workspace__utility-stack" gap={0}>{agent}{digests}</Stack>
    </section>
    <section className="feed-workspace__articles" aria-label="Articles">{articles}</section>
  </div>;
}
