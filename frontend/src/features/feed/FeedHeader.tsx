import { Badge, Button, Group, NumberInput, Text } from "@mantine/core";
import { PageHeader } from "../../components/ui/PageHeader";

export function FeedHeader({
  fetchLimit,
  runLimit,
  onRunLimitChange,
  onUpdate,
  loading,
  runStatus,
}: {
  fetchLimit: number;
  runLimit: number | string;
  onRunLimitChange: (value: number | string) => void;
  onUpdate: () => void;
  loading: boolean;
  runStatus?: string;
}) {
  return <Group justify="space-between" mb="md" align="end">
    <PageHeader title="Feed" description="Latest articles from configured news sources" />
    <Group align="end">
      <NumberInput label="Articles per update" min={1} max={100} value={runLimit} placeholder={String(fetchLimit)} onChange={onRunLimitChange} w={150} />
      {runStatus ? <Group gap="xs" align="center"><Text size="xs" c="dimmed">Run</Text><Badge color={runStatus === "failed" ? "red" : runStatus === "success" ? "green" : "blue"}>{runStatus}</Badge></Group> : null}
      <Button onClick={onUpdate} loading={loading} disabled={loading || runStatus === "pending" || runStatus === "running"}>Update feed</Button>
    </Group>
  </Group>;
}
