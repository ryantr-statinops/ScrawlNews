import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Group, Pagination, Text, Drawer, Anchor } from "@mantine/core";
import { useFeedQuery } from "../features/feed/hooks";
import { fetchConfig, fetchDigests, triggerRun } from "../lib/api";
import { FeedTable } from "../features/feed/FeedTable";
import { FeedHeader } from "../features/feed/FeedHeader";
import { FeedFilters } from "../features/feed/FeedFilters";
import { FeedWorkspace } from "../features/feed/FeedWorkspace";
import { DigestPanel } from "../features/feed/DigestPanel";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";
import type { Article, Digest } from "../types/api";
import { MarkdownContent } from "../components/ui/MarkdownContent";
import { AgentMockPanel } from "../features/feed/AgentMockPanel";

const PAGE_SIZE = 20;

export function FeedPage() {
  const queryClient = useQueryClient();
  const [q, setQ] = useState("");
  const [source, setSource] = useState<string | null>(null);
  const [category, setCategory] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [submitted, setSubmitted] = useState({ q: "", source: "", category: "" });
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [submittedDates, setSubmittedDates] = useState({ from: "", to: "" });
  const [runLimit, setRunLimit] = useState<number | string>("");
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  const configQuery = useQuery({ queryKey: ["config"], queryFn: fetchConfig });
  const digestQuery = useQuery({ queryKey: ["digests"], queryFn: () => fetchDigests() });
  const configuredFetchLimit = Number(configQuery.data?.fetch_limit ?? 20);
  const updateFeed = useMutation({
    mutationFn: () => triggerRun(
      runLimit === "" ? configuredFetchLimit : Number(runLimit),
      category ? [category] : undefined,
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    },
  });
  const categories: string[] = String(configQuery.data?.news_categories ?? "technology,business,world,science")
    .split(",")
    .map((c: string) => c.trim())
    .filter(Boolean);

  const params: Record<string, string> = {
    limit: String(PAGE_SIZE),
    offset: String((page - 1) * PAGE_SIZE),
  };
  if (submitted.q) params.q = submitted.q;
  if (submitted.source) params.source = submitted.source;
  if (submitted.category) params.category = submitted.category;
  if (submittedDates.from) params.from = `${submittedDates.from}T00:00:00Z`;
  if (submittedDates.to) params.to = `${submittedDates.to}T23:59:59Z`;

  const { data, isLoading, error } = useFeedQuery(params);
  const articles = data?.articles ?? [];
  const total = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const sources = Array.from(new Set(articles.map((a) => a.source).filter(Boolean))) as string[];
  const digests: Digest[] = digestQuery.data?.digests ?? [];

  const search = () => {
    setPage(1);
    setSubmitted({ q, source: source ?? "", category: category ?? "" });
    setSubmittedDates({ from: fromDate, to: toDate });
  };

  return (
    <div>
      <FeedHeader fetchLimit={configuredFetchLimit} runLimit={runLimit} onRunLimitChange={setRunLimit} onUpdate={() => updateFeed.mutate()} loading={updateFeed.isPending} />
      <FeedFilters q={q} source={source} category={category} sources={sources} categories={categories} fromDate={fromDate} toDate={toDate} onQueryChange={setQ} onSourceChange={setSource} onCategoryChange={setCategory} onFromChange={setFromDate} onToChange={setToDate} onSearch={search} loading={isLoading} />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      <FeedWorkspace
        articles={<>
          {!isLoading && !error && articles.length === 0 ? <EmptyState message="No articles found" /> : null}
          {articles.length > 0 ? <FeedTable articles={articles} onSelect={setSelectedArticle} /> : null}
          <AgentMockPanel />
        </>}
        digests={<DigestPanel digests={digests} />}
      />
      <Drawer opened={selectedArticle !== null} onClose={() => setSelectedArticle(null)} title={selectedArticle?.title} position="right" size="lg">
        {selectedArticle ? (
          <>
            <Text size="sm" c="dimmed" mb="md">{selectedArticle.source ?? "Unknown source"} · {selectedArticle.category ?? "uncategorized"}</Text>
            <Text size="sm" mb="md">Published: {selectedArticle.published_at ? new Date(selectedArticle.published_at).toLocaleString() : "-"}</Text>
            <MarkdownContent content={selectedArticle.content || "No extracted content available."} />
            <Anchor href={selectedArticle.url} target="_blank" rel="noreferrer">Open original article</Anchor>
          </>
        ) : null}
      </Drawer>
      {totalPages > 1 ? (
        <Group justify="space-between" mt="md">
          <Text size="sm" c="dimmed">
            Total: {total} · Page {page} / {totalPages}
          </Text>
          <Pagination total={totalPages} value={page} onChange={setPage} />
        </Group>
      ) : null}
    </div>
  );
}
