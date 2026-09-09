import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Group, Stack, Switch, Table, TextInput, Text } from "@mantine/core";
import { createSource, fetchSources, updateSource } from "../lib/api";

type Source = { id: string; name: string; url: string; category: string | null; enabled: number };

export function SourceManager() {
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const sourcesQuery = useQuery({ queryKey: ["sources", query], queryFn: () => fetchSources(query) });
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["sources"] });
  const toggle = useMutation({ mutationFn: ({ source, enabled }: { source: Source; enabled: boolean }) => updateSource(source.id, { enabled }), onSuccess: refresh });
  const add = useMutation({
    mutationFn: () => createSource({ name, url, enabled: true }),
    onSuccess: () => { setName(""); setUrl(""); refresh(); },
  });
  const test = useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`/api/sources/${id}/test`, { method: "POST" });
      if (!res.ok) throw new Error(`Source test failed: ${res.status}`);
      return res.json();
    },
    onSuccess: refresh,
  });
  const sources: Source[] = sourcesQuery.data?.sources ?? [];

  return (
    <Card shadow="sm" mt="lg">
      <Text fw={600} mb="xs">News sources</Text>
      <Group mb="md">
        <TextInput placeholder="Search catalog" value={query} onChange={(e) => setQuery(e.currentTarget.value)} />
        <TextInput placeholder="Custom source name" value={name} onChange={(e) => setName(e.currentTarget.value)} />
        <TextInput placeholder="RSS/Atom URL" value={url} onChange={(e) => setUrl(e.currentTarget.value)} />
        <Button onClick={() => add.mutate()} loading={add.isPending} disabled={!name || !url}>Add</Button>
      </Group>
      {sourcesQuery.error ? <Text c="red">{(sourcesQuery.error as Error).message}</Text> : null}
      <Table striped highlightOnHover>
        <Table.Thead><Table.Tr><Table.Th>Source</Table.Th><Table.Th>Category</Table.Th><Table.Th>Enabled</Table.Th><Table.Th>Test</Table.Th></Table.Tr></Table.Thead>
        <Table.Tbody>{sources.map((source) => (
          <Table.Tr key={source.id}>
            <Table.Td><Stack gap={0}><Text>{source.name}</Text><Text size="xs" c="dimmed">{source.url}</Text></Stack></Table.Td>
            <Table.Td>{source.category ?? "custom"}</Table.Td>
            <Table.Td><Switch checked={Boolean(source.enabled)} onChange={(e) => toggle.mutate({ source, enabled: e.currentTarget.checked })} /></Table.Td>
            <Table.Td><Button size="xs" variant="light" onClick={() => test.mutate(source.id)} loading={test.isPending}>Test</Button></Table.Td>
          </Table.Tr>
        ))}</Table.Tbody>
      </Table>
    </Card>
  );
}
