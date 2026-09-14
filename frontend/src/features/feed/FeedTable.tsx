import { Badge, Card, Group, Stack, Text, Title } from "@mantine/core";
import type { Article } from "../../types/api";
import "./FeedTable.css";

export function FeedTable({ articles, onSelect }: { articles: Article[]; onSelect?: (article: Article) => void }) {
  return (
    <Stack gap="sm" className="feed-article-list">
      {articles.map((a) => {
        const open = () => onSelect?.(a);
        return (
          <Card key={a.id} withBorder shadow="xs" padding="lg" className="feed-article-card" tabIndex={onSelect ? 0 : undefined} role={onSelect ? "button" : undefined} aria-label={onSelect ? `Open article: ${a.title}` : undefined} onClick={open} onKeyDown={(event) => { if (onSelect && (event.key === "Enter" || event.key === " ")) { event.preventDefault(); open(); } }}>
            <Stack gap="xs">
              <Group justify="space-between" align="start" gap="sm" wrap="nowrap">
                <Title order={4} className="feed-article-card__title">{a.title}</Title>
                <Badge color={a.summarized ? "green" : "yellow"} variant="light" className="feed-article-card__status">{a.summarized ? "Summarized" : "Pending"}</Badge>
              </Group>
              <Group gap="xs" c="dimmed" fz="sm">
                <Text span fw={600}>{a.source ?? "Unknown source"}</Text>
                <Text span>·</Text>
                <Text span>{a.category ?? "Uncategorized"}</Text>
              </Group>
              <Text size="xs" c="dimmed">Published {a.published_at ? new Date(a.published_at).toLocaleString() : "not available"}</Text>
            </Stack>
          </Card>
        );
      })}
    </Stack>
  );
}
