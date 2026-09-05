import { Title, Text, Stack } from "@mantine/core";

interface PageHeaderProps {
  title: string;
  description?: string;
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <Stack gap="xs" mb="md">
      <Title order={2}>{title}</Title>
      {description ? (
        <Text c="dimmed" size="sm">
          {description}
        </Text>
      ) : null}
    </Stack>
  );
}
