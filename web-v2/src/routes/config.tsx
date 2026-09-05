import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, zodResolver } from "@mantine/form";
import { NumberInput, TextInput, Switch, Button, Stack, Card } from "@mantine/core";
import { z } from "zod";
import { fetchConfig, updateConfig } from "../lib/api";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";

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
    </div>
  );
}
