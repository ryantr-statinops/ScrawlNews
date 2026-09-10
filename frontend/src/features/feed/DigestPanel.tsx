import { Alert, Badge, Button, Card, Group, Loader, SimpleGrid, Text, Title } from "@mantine/core";
import type { Digest } from "../../types/api";
import { MarkdownContent } from "../../components/ui/MarkdownContent";
import "./DigestPanel.css";

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

export function DigestPanel({ digests, onSelect, loading = false, error }: { digests: Digest[]; onSelect?: (digest: Digest) => void; loading?: boolean; error?: string }) {
  const latestDigests = latestDigestsByCategory(digests);
  return <Card withBorder className="digest-panel" style={{ maxHeight: "70vh", overflowY: "auto" }}>
    <Title order={4} mb="sm">Topic digests</Title>
    {loading ? <Loader size="sm" /> : null}
    {error ? <Alert color="red" title="Unable to load digests">{error}</Alert> : null}
    {!loading && !error && latestDigests.length === 0 ? <Text c="dimmed">No topic digests yet.</Text> : null}
    {!loading && !error && latestDigests.length > 0 ? <SimpleGrid cols={1}>{latestDigests.map((digest) => <Card key={digest.id} withBorder shadow="xs" onClick={() => onSelect?.(digest)} style={{ cursor: onSelect ? "pointer" : undefined }}><Group justify="space-between" gap="xs"><Text fw={600}>{digest.title}</Text>{digest.status !== "success" ? <Badge color="red">{digest.status}</Badge> : null}</Group><Text size="sm" c="dimmed" mb="xs">{digest.category} · {digest.article_count} articles</Text>{digest.error ? <Text size="xs" c="red" mb="xs">{digest.error}</Text> : null}<div className="digest-panel__preview"><MarkdownContent content={digest.digest_text || "No digest content available."} /></div>{onSelect ? <Button variant="subtle" size="compact-sm" mt="sm" onClick={() => onSelect(digest)}>Open digest</Button> : null}</Card>)}</SimpleGrid> : null}
  </Card>;
}
