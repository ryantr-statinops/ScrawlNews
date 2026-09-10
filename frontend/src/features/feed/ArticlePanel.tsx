import type { ReactNode } from "react";
import { Card, Group, Text, Title } from "@mantine/core";

export function ArticlePanel({ children, footer, total }: { children: ReactNode; footer?: ReactNode; total: number }) {
  return <Card withBorder padding={0}>
    <Group justify="space-between" p="md" pb="sm">
      <Title order={4}>Articles</Title>
      <Text size="sm" c="dimmed">{total} result{total === 1 ? "" : "s"}</Text>
    </Group>
    {children}
    {footer ? <Card.Section withBorder inheritPadding py="sm">{footer}</Card.Section> : null}
  </Card>;
}
