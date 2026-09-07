import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { TextInput, Select, Button, Group, Pagination, Text } from "@mantine/core";
import { useFeedQuery } from "../features/feed/hooks";
import { fetchConfig } from "../lib/api";
import { FeedTable } from "../features/feed/FeedTable";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";

const PAGE_SIZE = 20;

export function FeedPage() {
  const [q, setQ] = useState("");
  const [source, setSource] = useState<string | null>(null);
  const [category, setCategory] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [submitted, setSubmitted] = useState({ q: "", source: "", category: "" });

  const configQuery = useQuery({ queryKey: ["config"], queryFn: fetchConfig });
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

  const { data, isLoading, error } = useFeedQuery(params);
  const articles = data?.articles ?? [];
  const total = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const sources = Array.from(new Set(articles.map((a) => a.source).filter(Boolean))) as string[];

  const search = () => {
    setPage(1);
    setSubmitted({ q, source: source ?? "", category: category ?? "" });
  };

  return (
    <div>
      <PageHeader title="Feed" description="Latest articles from Google News RSS" />
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
        <Button onClick={search} loading={isLoading}>
          Search
        </Button>
      </Group>
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
