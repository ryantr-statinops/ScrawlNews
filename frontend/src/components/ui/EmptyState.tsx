import { Center, Text } from "@mantine/core";

export function EmptyState({ message = "No data" }: { message?: string }) {
  return (
    <Center py="xl">
      <Text c="dimmed">{message}</Text>
    </Center>
  );
}
