import { Card, SimpleGrid, Text, Title } from "@mantine/core";
import type { Digest } from "../../types/api";
import { MarkdownContent } from "../../components/ui/MarkdownContent";

export function DigestPanel({ digests }: { digests: Digest[] }) {
  return <Card withBorder style={{ maxHeight: "70vh", overflowY: "auto" }}>
    <Title order={4} mb="sm">Topic digests</Title>
    {digests.length === 0 ? <Text c="dimmed">No topic digests yet.</Text> : <SimpleGrid cols={1}>{digests.map((digest) => <Card key={digest.id} withBorder shadow="xs"><Text fw={600}>{digest.title}</Text><Text size="sm" c="dimmed" mb="xs">{digest.category} · {digest.article_count} articles</Text><MarkdownContent content={digest.digest_text} /></Card>)}</SimpleGrid>}
  </Card>;
}
