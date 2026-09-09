import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { TextInput, Select, Button, Group, Pagination, Text, NumberInput, Card, SimpleGrid, Title } from "@mantine/core";
import { useFeedQuery } from "../features/feed/hooks";
import { fetchConfig, fetchDigests, triggerRun } from "../lib/api";
import { FeedTable } from "../features/feed/FeedTable";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";
import type { Digest } from "../types/api";

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
      <Group justify="space-between" mb="md" align="end">
        <PageHeader title="Feed" description="Latest articles from configured news sources" />
        <Group align="end">
          <NumberInput
            label="Articles per update"
            min={1}
            max={100}
            value={runLimit}
            placeholder={String(configuredFetchLimit)}
            onChange={setRunLimit}
            w={150}
          />
          <Button onClick={() => updateFeed.mutate()} loading={updateFeed.isPending}>
            Update feed
          </Button>
        </Group>
      </Group>
      <Group mb="md">
        <TextInput
          placeholder="Search..."
          value={q}
          onChange={(e) => setQ(e.currentTarget.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
        />
        <Select
          placeholder="All sources"
          clearable
          data={sources}
          value={source}
          onChange={setSource}
        />
        <Select
          placeholder="All categories"
          clearable
          data={categories}
          value={category}
          onChange={setCategory}
        />
        <TextInput type="date" label="From" value={fromDate} onChange={(e) => setFromDate(e.currentTarget.value)} />
        <TextInput type="date" label="To" value={toDate} onChange={(e) => setToDate(e.currentTarget.value)} />
        <Button onClick={search} loading={isLoading}>
          Search
        </Button>
      </Group>
      {digests.length > 0 ? (
        <Card withBorder mb="md">
          <Title order={4} mb="sm">Topic digests</Title>
          <SimpleGrid cols={{ base: 1, md: 2 }}>
            {digests.map((digest) => (
              <Card key={digest.id} withBorder shadow="xs">
                <Text fw={600}>{digest.title}</Text>
                <Text size="sm" c="dimmed" mb="xs">
                  {digest.category} · {digest.article_count} articles
                </Text>
                <Text size="sm">{digest.digest_text}</Text>
              </Card>
            ))}
          </SimpleGrid>
        </Card>
      ) : null}
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {!isLoading && !error && articles.length === 0 ? <EmptyState message="No articles found" /> : null}
      {articles.length > 0 ? <FeedTable articles={articles} /> : null}
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
