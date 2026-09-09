import { useQuery } from "@tanstack/react-query";
import { Group, ScrollArea, Tabs } from "@mantine/core";
import { Activity, BarChart3, Bot, RadioTower, Workflow } from "lucide-react";
import { PageHeader } from "../components/ui/PageHeader";
import { AnalyticsFilters } from "../features/analytics/AnalyticsFilters";
import { analyticsApi } from "../features/analytics/api";
import { AiUsageTab } from "../features/analytics/AiUsageTab";
import { ContentTab } from "../features/analytics/ContentTab";
import { OverviewTab } from "../features/analytics/OverviewTab";
import { PipelineTab } from "../features/analytics/PipelineTab";
import { SourcesTab } from "../features/analytics/SourcesTab";
import type { AnalyticsTab } from "../features/analytics/types";
import { useAnalyticsFilters } from "../features/analytics/useAnalyticsFilters";

export function AnalyticsPage() {
  const { filters, setFilters, tab, setTab } = useAnalyticsFilters();
  const content = useQuery({ queryKey: ["analytics", "content", filters], queryFn: () => analyticsApi.content(filters) });
  const usage = useQuery({ queryKey: ["analytics", "ai-usage", filters], queryFn: () => analyticsApi.aiUsage(filters) });
  const categories = (content.data?.categories ?? []).map((row) => String(row.category));
  const sources = (content.data?.sources ?? []).map((row) => String(row.source));
  const providers = (usage.data?.providers ?? []).map((row) => String(row.provider));
  const models = (usage.data?.models ?? []).map((row) => String(row.model));

  return (
    <div>
      <Group justify="space-between" align="start" mb="md" gap="md" wrap="wrap">
        <PageHeader title="Analytics Command Center" description="News intelligence, pipeline operations and AI usage in one place" />
        <AnalyticsFilters value={filters} onChange={setFilters} categories={categories} sources={sources} providers={providers} models={models} />
      </Group>
      <Tabs value={tab} onChange={(value) => setTab((value ?? "overview") as AnalyticsTab)} keepMounted={false}>
        <ScrollArea type="auto" mb="md">
          <Tabs.List style={{ flexWrap: "nowrap", minWidth: "max-content" }}>
            <Tabs.Tab value="overview" leftSection={<Activity size={15} />}>Overview</Tabs.Tab>
            <Tabs.Tab value="content" leftSection={<BarChart3 size={15} />}>Content</Tabs.Tab>
            <Tabs.Tab value="pipeline" leftSection={<Workflow size={15} />}>Pipeline</Tabs.Tab>
            <Tabs.Tab value="sources" leftSection={<RadioTower size={15} />}>Sources</Tabs.Tab>
            <Tabs.Tab value="ai-usage" leftSection={<Bot size={15} />}>AI Usage</Tabs.Tab>
          </Tabs.List>
        </ScrollArea>
        <Tabs.Panel value="overview"><OverviewTab filters={filters} /></Tabs.Panel>
        <Tabs.Panel value="content"><ContentTab filters={filters} /></Tabs.Panel>
        <Tabs.Panel value="pipeline"><PipelineTab filters={filters} /></Tabs.Panel>
        <Tabs.Panel value="sources"><SourcesTab filters={filters} /></Tabs.Panel>
        <Tabs.Panel value="ai-usage"><AiUsageTab filters={filters} /></Tabs.Panel>
      </Tabs>
    </div>
  );
}
