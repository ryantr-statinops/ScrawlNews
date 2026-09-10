import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Group, Pagination, Text, Drawer, Anchor, Stack } from "@mantine/core";
import { useFeedQuery } from "../features/feed/hooks";
import { fetchConfig, fetchDigestArticles, fetchDigests, fetchRuns, fetchSources, fetchSummaries, triggerRun } from "../lib/api";
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
import { ArticlePanel } from "../features/feed/ArticlePanel";

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
  const [selectedDigest, setSelectedDigest] = useState<Digest | null>(null);

  const configQuery = useQuery({ queryKey: ["config"], queryFn: fetchConfig });
  const digestQuery = useQuery({ queryKey: ["digests"], queryFn: () => fetchDigests() });
  const runsQuery = useQuery({ queryKey: ["runs"], queryFn: fetchRuns, refetchInterval: 5000 });
  const sourcesQuery = useQuery({ queryKey: ["sources"], queryFn: () => fetchSources() });
  const articleSummariesQuery = useQuery({ queryKey: ["summaries", selectedArticle?.id], queryFn: () => fetchSummaries(selectedArticle!.id), enabled: selectedArticle !== null });
  const digestArticlesQuery = useQuery({ queryKey: ["digest-articles", selectedDigest?.id], queryFn: () => fetchDigestArticles(selectedDigest!.id), enabled: selectedDigest !== null });
  const configuredFetchLimit = Number(configQuery.data?.fetch_limit ?? 20);
  const updateFeed = useMutation({
    mutationFn: () => triggerRun(
      runLimit === "" ? configuredFetchLimit : Number(runLimit),
      category ? [category] : undefined,
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
      queryClient.invalidateQueries({ queryKey: ["articles"] });
      queryClient.invalidateQueries({ queryKey: ["digests"] });
    },
  });
  const latestRun = runsQuery.data?.runs?.[0];
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
  const sources = Array.from(new Set((sourcesQuery.data?.sources ?? []).map((source: { name: string }) => source.name).filter(Boolean))) as string[];
  const digests: Digest[] = digestQuery.data?.digests ?? [];

  const search = () => {
    setPage(1);
    setSubmitted({ q, source: source ?? "", category: category ?? "" });
    setSubmittedDates({ from: fromDate, to: toDate });
  };

  return (
    <div>
      <FeedHeader fetchLimit={configuredFetchLimit} runLimit={runLimit} onRunLimitChange={setRunLimit} onUpdate={() => updateFeed.mutate()} loading={updateFeed.isPending} runStatus={latestRun?.status} />
      <FeedFilters q={q} source={source} category={category} sources={sources} categories={categories} fromDate={fromDate} toDate={toDate} onQueryChange={setQ} onSourceChange={setSource} onCategoryChange={setCategory} onFromChange={setFromDate} onToChange={setToDate} onSearch={search} loading={isLoading} />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      <FeedWorkspace
        articles={<ArticlePanel total={total} footer={totalPages > 1 ? (
          <Group justify="space-between">
            <Text size="sm" c="dimmed">Page {page} / {totalPages}</Text>
            <Pagination total={totalPages} value={page} onChange={setPage} />
          </Group>
        ) : null}>
          {!isLoading && !error && articles.length === 0 ? <EmptyState message="No articles found" /> : null}
          {articles.length > 0 ? <FeedTable articles={articles} onSelect={setSelectedArticle} /> : null}
        </ArticlePanel>}
        digests={<DigestPanel digests={digests} onSelect={setSelectedDigest} loading={digestQuery.isLoading} error={digestQuery.error ? (digestQuery.error as Error).message : undefined} />}
        agent={<AgentMockPanel />}
      />
      <Drawer opened={selectedArticle !== null} onClose={() => setSelectedArticle(null)} title={selectedArticle?.title} position="right" size="lg">
        {selectedArticle ? (
          <>
            <Text size="sm" c="dimmed" mb="md">{selectedArticle.source ?? "Unknown source"} · {selectedArticle.category ?? "uncategorized"}</Text>
            <Text size="sm" mb="md">Published: {selectedArticle.published_at ? new Date(selectedArticle.published_at).toLocaleString() : "-"}</Text>
            <Text size="sm" mb="md">Fetched: {selectedArticle.fetched_at ? new Date(selectedArticle.fetched_at).toLocaleString() : "-"}</Text>
            <Text fw={600}>Related summary</Text>
            {articleSummariesQuery.isLoading ? <Text size="sm" c="dimmed">Loading summary...</Text> : null}
            {articleSummariesQuery.error ? <Text size="sm" c="red">Unable to load summary.</Text> : null}
            {!articleSummariesQuery.isLoading && !articleSummariesQuery.error && !articleSummariesQuery.data?.summaries?.length ? <Text size="sm" c="dimmed">No summary available.</Text> : null}
            {articleSummariesQuery.data?.summaries?.[0] ? <MarkdownContent content={articleSummariesQuery.data.summaries[0].summary_text} /> : null}
            <MarkdownContent content={selectedArticle.content || "No extracted content available."} />
            <Anchor href={selectedArticle.url} target="_blank" rel="noreferrer">Open original article</Anchor>
          </>
        ) : null}
      </Drawer>
      <Drawer opened={selectedDigest !== null} onClose={() => setSelectedDigest(null)} title={selectedDigest?.title} position="left" size="lg">
        {selectedDigest ? (
          <Stack gap="md">
            <Text size="sm" c="dimmed">{selectedDigest.category} · {selectedDigest.article_count} articles · {selectedDigest.created_at ? new Date(selectedDigest.created_at).toLocaleString() : "-"}</Text>
            <Text size="sm">Model: {selectedDigest.model_used || "-"}</Text>
            <Text size="sm">Status: {selectedDigest.status}</Text>
            {selectedDigest.error ? <Text size="sm" c="red">{selectedDigest.error}</Text> : null}
            <MarkdownContent content={selectedDigest.digest_text} />
            <Text fw={600}>Source articles</Text>
            {digestArticlesQuery.isLoading ? <Text size="sm" c="dimmed">Loading source articles...</Text> : null}
            {digestArticlesQuery.error ? <Text size="sm" c="red">Unable to load source articles.</Text> : null}
            {digestArticlesQuery.data?.articles?.map((article: Article) => <Anchor key={article.id} component="button" type="button" onClick={() => { setSelectedDigest(null); setSelectedArticle(article); }}>{article.title}</Anchor>)}
            <Text fw={600}>Earlier digests in this category</Text>
            {digests.filter((digest) => digest.category === selectedDigest.category && digest.id !== selectedDigest.id).map((digest) => (
              <Anchor key={digest.id} component="button" type="button" onClick={() => setSelectedDigest(digest)}>{digest.title} · {digest.created_at ? new Date(digest.created_at).toLocaleDateString() : "-"}</Anchor>
            ))}
          </Stack>
        ) : null}
      </Drawer>
    </div>
  );
}
