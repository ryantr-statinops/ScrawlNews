import { Button, Group, NumberInput } from "@mantine/core";
import { PageHeader } from "../../components/ui/PageHeader";

export function FeedHeader({
  fetchLimit,
  runLimit,
  onRunLimitChange,
  onUpdate,
  loading,
}: {
  fetchLimit: number;
  runLimit: number | string;
  onRunLimitChange: (value: number | string) => void;
  onUpdate: () => void;
  loading: boolean;
}) {
  return <Group justify="space-between" mb="md" align="end">
    <PageHeader title="Feed" description="Latest articles from configured news sources" />
    <Group align="end">
      <NumberInput label="Articles per update" min={1} max={100} value={runLimit} placeholder={String(fetchLimit)} onChange={onRunLimitChange} w={150} />
      <Button onClick={onUpdate} loading={loading}>Update feed</Button>
    </Group>
  </Group>;
}
