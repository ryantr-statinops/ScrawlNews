import { Card, SimpleGrid, Text, Title } from "@mantine/core";
import type { Digest } from "../../types/api";
import { MarkdownContent } from "../../components/ui/MarkdownContent";

export function latestDigestsByCategory(digests: Digest[]) {
  const newest = new Map<string, Digest>();
  for (const digest of digests) {
    const existing = newest.get(digest.category);
    if (!existing || new Date(digest.created_at ?? 0).getTime() > new Date(existing.created_at ?? 0).getTime()) {
      newest.set(digest.category, digest);
    }
  }
  return [...newest.values()].sort((a, b) => new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime());
}

export function DigestPanel({ digests, onSelect }: { digests: Digest[]; onSelect?: (digest: Digest) => void }) {
  const latestDigests = latestDigestsByCategory(digests);
  return <Card withBorder className="digest-panel" style={{ maxHeight: "70vh", overflowY: "auto" }}>
    <Title order={4} mb="sm">Topic digests</Title>
    {latestDigests.length === 0 ? <Text c="dimmed">No topic digests yet.</Text> : <SimpleGrid cols={1}>{latestDigests.map((digest) => <Card key={digest.id} withBorder shadow="xs" onClick={() => onSelect?.(digest)} style={{ cursor: onSelect ? "pointer" : undefined }}><Text fw={600}>{digest.title}</Text><Text size="sm" c="dimmed" mb="xs">{digest.category} · {digest.article_count} articles</Text><MarkdownContent content={digest.digest_text} /></Card>)}</SimpleGrid>}
  </Card>;
}
