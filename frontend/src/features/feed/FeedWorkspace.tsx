import type { ReactNode } from "react";
import { SimpleGrid } from "@mantine/core";

export function FeedWorkspace({ articles, digests, agent }: { articles: ReactNode; digests: ReactNode; agent: ReactNode }) {
  return <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md" style={{ alignItems: "start" }}>
    <section aria-label="Feed tools">{agent}{digests}</section>
    <section aria-label="Articles">{articles}</section>
  </SimpleGrid>;
}
