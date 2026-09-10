import type { ReactNode } from "react";
import { Card, Group, Text, Title } from "@mantine/core";

export function ArticlePanel({ children, total }: { children: ReactNode; total: number }) {
  return <Card withBorder padding={0}>
    <Group justify="space-between" p="md" pb="sm">
      <Title order={4}>Articles</Title>
      <Text size="sm" c="dimmed">{total} result{total === 1 ? "" : "s"}</Text>
    </Group>
    {children}
  </Card>;
}
