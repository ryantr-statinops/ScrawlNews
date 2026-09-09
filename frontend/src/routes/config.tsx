import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, zodResolver } from "@mantine/form";
import { NumberInput, TextInput, Switch, Button, Stack, Card, Table, Title } from "@mantine/core";
import { z } from "zod";
import { fetchConfig, updateConfig } from "../lib/api";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { SourceManager } from "../components/SourceManager";

const schema = z.object({
  fetch_limit: z.number().min(1).max(100),
  summary_lang: z.string().min(2).max(5),
  telegram_enabled: z.boolean(),
  retention_days: z.number().min(1).max(30),
});

export function ConfigPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({ queryKey: ["config"], queryFn: fetchConfig });
  const save = useMutation({
    mutationFn: updateConfig,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["config"] }),
  });

  const form = useForm({
    initialValues: {
      fetch_limit: data?.fetch_limit ?? 20,
      summary_lang: data?.summary_lang ?? "vi",
      telegram_enabled: data?.telegram_enabled ?? true,
      retention_days: data?.retention_days ?? 7,
    },
    validate: zodResolver(schema),
  });

  const historyQuery = useQuery({
    queryKey: ["config-history"],
    queryFn: async () => {
      const res = await fetch("/api/config/history?limit=20");
      if (!res.ok) throw new Error(`Failed: ${res.status}`);
      return res.json();
    },
  });
  const history: { key: string; old_value: string | null; new_value: string; changed_at: string }[] =
    historyQuery.data?.history ?? [];

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={(error as Error).message} />;

  return (
    <div>
      <PageHeader title="Config" description="Hot-reload 4 vars (secrets require restart)" />
      <Card shadow="sm">
        <form onSubmit={form.onSubmit((v) => save.mutate(v))}>
          <Stack>
            <NumberInput label="Fetch limit" {...form.getInputProps("fetch_limit")} />
            <TextInput label="Summary lang" {...form.getInputProps("summary_lang")} />
            <Switch label="Telegram enabled" {...form.getInputProps("telegram_enabled", { type: "checkbox" })} />
            <NumberInput label="Retention days" {...form.getInputProps("retention_days")} />
            <Button type="submit" loading={save.isPending}>
              Save
            </Button>
          </Stack>
        </form>
      </Card>
      <SourceManager />
      <Title order={4} mt="lg" mb="xs">
        Change history
      </Title>
      {history.length > 0 ? (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Key</Table.Th>
              <Table.Th>Old</Table.Th>
              <Table.Th>New</Table.Th>
              <Table.Th>Changed</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {history.map((h, i) => (
              <Table.Tr key={i}>
                <Table.Td>{h.key}</Table.Td>
                <Table.Td>{h.old_value ?? "-"}</Table.Td>
                <Table.Td>{h.new_value}</Table.Td>
                <Table.Td>{h.changed_at ? new Date(h.changed_at).toLocaleString() : "-"}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      ) : null}
    </div>
  );
}
