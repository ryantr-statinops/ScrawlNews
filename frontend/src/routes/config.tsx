import { useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, zodResolver } from "@mantine/form";
import { Alert, NumberInput, Textarea, TextInput, Switch, Button, Stack, Card, Table, Title, Group, Badge, Text } from "@mantine/core";
import { z } from "zod";
import { ApiError } from "../lib/api";
import { fetchConfig, fetchConfigHistory, updateConfig } from "../lib/api";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { SourceManager } from "../components/SourceManager";

const scheduleTimes = z.string().refine((value) => {
  const entries = value.split(",");
  return entries.length > 0 && entries.every((entry) => /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(entry)) &&
    new Set(entries).size === entries.length;
}, "Use unique HH:MM times separated by commas");
const timezone = z.string().min(1).refine((value) => {
  try { new Intl.DateTimeFormat("en", { timeZone: value }); return true; }
  catch { return false; }
}, "Enter a valid IANA timezone");

const schema = z.object({
  fetch_limit: z.number().min(1).max(100),
  summary_lang: z.string().min(2).max(5),
  telegram_enabled: z.boolean(),
  retention_days: z.number().min(1).max(30),
  schedule_times: scheduleTimes,
  schedule_timezone: timezone,
  news_country: z.string().min(2),
  news_city: z.string().min(2),
  llm_price_snapshot_json: z.string().refine((value) => {
    try {
      const parsed: unknown = JSON.parse(value);
      return parsed !== null && typeof parsed === "object" && !Array.isArray(parsed);
    } catch { return false; }
  }, "Enter a JSON object of provider/model prices"),
  llm_monthly_budget_usd: z.number().finite().min(0),
});

export function ConfigPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery({ queryKey: ["config"], queryFn: fetchConfig });
  const save = useMutation({
    mutationFn: updateConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["config"] });
      queryClient.invalidateQueries({ queryKey: ["config-history"] });
    },
  });

  const form = useForm({
    initialValues: {
      fetch_limit: data?.fetch_limit ?? 20,
      summary_lang: data?.summary_lang ?? "vi",
      telegram_enabled: data?.telegram_enabled ?? true,
      retention_days: data?.retention_days ?? 7,
      schedule_times: data?.schedule_times ?? "08:00,12:00,18:00",
      schedule_timezone: data?.schedule_timezone ?? "Asia/Ho_Chi_Minh",
      news_country: data?.news_country ?? "VN",
      news_city: data?.news_city ?? "Hanoi",
      llm_price_snapshot_json: data?.llm_price_snapshot_json ?? "{}",
      llm_monthly_budget_usd: data?.llm_monthly_budget_usd ?? 0,
    },
    validate: zodResolver(schema),
  });
  useEffect(() => {
    if (data && !form.isDirty()) form.setValues({
      fetch_limit: data.fetch_limit,
      summary_lang: data.summary_lang,
      telegram_enabled: data.telegram_enabled,
      retention_days: data.retention_days,
      schedule_times: data.schedule_times,
      schedule_timezone: data.schedule_timezone,
      news_country: data.news_country,
      news_city: data.news_city,
      llm_price_snapshot_json: data.llm_price_snapshot_json,
      llm_monthly_budget_usd: data.llm_monthly_budget_usd,
    });
  }, [data]);

  const historyQuery = useQuery({
    queryKey: ["config-history"],
    queryFn: async () => {
      return fetchConfigHistory();
    },
  });
  const history: { key: string; old_value: string | null; new_value: string; changed_at: string }[] =
    historyQuery.data?.history ?? [];

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={(error as Error).message} />;

  return (
    <div>
      <PageHeader title="Settings" description="Reading, delivery, and schedule preferences" />
      <Card withBorder mb="md">
        <Text fw={600} mb="xs">Connected services</Text>
        <Group gap="sm">
          <Badge variant="light">Model: {data?.llm_provider} / {data?.llm_model}</Badge>
          <Badge color={data?.llm_configured ? "teal" : "gray"} variant="light">
            AI {data?.llm_configured ? "configured" : "fallback mode"}
          </Badge>
          <Badge color={data?.telegram_configured ? "teal" : "gray"} variant="light">
            Telegram {data?.telegram_configured ? "configured" : "not configured"}
          </Badge>
        </Group>
        <Text size="xs" c="dimmed" mt="xs">Credentials are kept outside the browser and are never shown here.</Text>
      </Card>
      <Card shadow="sm">
        <form onSubmit={form.onSubmit((v) => save.mutate(v))}>
          <Stack>
            <NumberInput label="Fetch limit" {...form.getInputProps("fetch_limit")} />
            <TextInput label="Summary lang" {...form.getInputProps("summary_lang")} />
            <Switch label="Telegram enabled" {...form.getInputProps("telegram_enabled", { type: "checkbox" })} />
            <NumberInput label="Retention days" {...form.getInputProps("retention_days")} />
            <TextInput label="Daily update times" description="HH:MM values separated by commas" {...form.getInputProps("schedule_times")} />
            <TextInput label="Schedule timezone" {...form.getInputProps("schedule_timezone")} />
            <TextInput label="News country" {...form.getInputProps("news_country")} />
            <TextInput label="News city" {...form.getInputProps("news_city")} />
            <Textarea label="LLM price snapshot JSON" description="Prices per million input/output tokens, keyed by provider/model" autosize minRows={4} {...form.getInputProps("llm_price_snapshot_json")} />
            <NumberInput label="Monthly AI budget (USD)" description="0 disables budget warnings" min={0} decimalScale={6} {...form.getInputProps("llm_monthly_budget_usd")} />
            {save.error && <Alert color="red" title="Unable to save settings">{save.error instanceof ApiError ? save.error.message : "Unable to save settings"}</Alert>}
            <Button type="submit" loading={save.isPending}>
              Save
            </Button>
          </Stack>
        </form>
      </Card>
      <SourceManager />
      <Title order={4} mt="lg" mb="xs">
        Preference history
      </Title>
      {history.length > 0 ? (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Preference</Table.Th>
              <Table.Th>Previous</Table.Th>
              <Table.Th>Current</Table.Th>
              <Table.Th>Updated</Table.Th>
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
