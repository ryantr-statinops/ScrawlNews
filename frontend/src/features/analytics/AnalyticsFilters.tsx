import { Group, Select } from "@mantine/core";
import type { AnalyticsFiltersState, AnalyticsWindow } from "./types";

interface Props {
  value: AnalyticsFiltersState;
  onChange: (value: AnalyticsFiltersState) => void;
  categories: string[];
  sources: string[];
  providers: string[];
  models: string[];
}

const windowOptions = ["1h", "4h", "12h", "24h", "7d", "30d"].map((value) => ({
  value,
  label: `Last ${value}`,
}));

export function AnalyticsFilters({ value, onChange, categories, sources, providers, models }: Props) {
  const update = <K extends keyof AnalyticsFiltersState>(key: K, next: AnalyticsFiltersState[K]) =>
    onChange({ ...value, [key]: next });

  return (
    <Group gap="sm" align="end" wrap="wrap" aria-label="Analytics filters">
      <Select
        label="Window"
        value={value.window}
        data={windowOptions}
        onChange={(next) => update("window", (next ?? "24h") as AnalyticsWindow)}
        allowDeselect={false}
        w={120}
      />
      <Select label="Category" placeholder="All categories" clearable searchable value={value.category} data={categories} onChange={(next) => update("category", next)} w={170} />
      <Select label="Source" placeholder="All sources" clearable searchable value={value.sourceId} data={sources} onChange={(next) => update("sourceId", next)} w={190} />
      <Select label="Provider" placeholder="All providers" clearable searchable value={value.provider} data={providers} onChange={(next) => update("provider", next)} w={160} />
      <Select label="Model" placeholder="All models" clearable searchable value={value.model} data={models} onChange={(next) => update("model", next)} w={200} />
    </Group>
  );
}
