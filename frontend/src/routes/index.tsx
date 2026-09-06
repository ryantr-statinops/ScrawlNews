import { useState } from "react";
import { TextInput, Select, Button, Group, Pagination, Text } from "@mantine/core";
import { useFeedQuery } from "../features/feed/hooks";
import { FeedTable } from "../features/feed/FeedTable";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";

const PAGE_SIZE = 20;

export function FeedPage() {
  const [q, setQ] = useState("");
  const [source, setSource] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [submitted, setSubmitted] = useState({ q: "", source: "" });

  const params: Record<string, string> = {
    limit: String(PAGE_SIZE),
    offset: String((page - 1) * PAGE_SIZE),
  };
  if (submitted.q) params.q = submitted.q;
  if (submitted.source) params.source = submitted.source;

  const { data, isLoading, error } = useFeedQuery(params);
  const articles = data?.articles ?? [];
  const total = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const sources = Array.from(new Set(articles.map((a) => a.source).filter(Boolean))) as string[];

  const search = () => {
    setPage(1);
    setSubmitted({ q, source: source ?? "" });
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
