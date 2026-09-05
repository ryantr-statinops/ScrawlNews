import { useFeedQuery } from "../features/feed/hooks";
import { FeedTable } from "../features/feed/FeedTable";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";

export function FeedPage() {
  const { data, isLoading, error } = useFeedQuery({ limit: "20" });

  return (
    <div>
      <PageHeader title="Feed" description="Latest articles from Google News RSS" />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {data && data.articles.length === 0 ? <EmptyState message="No articles yet" /> : null}
      {data && data.articles.length > 0 ? <FeedTable articles={data.articles} /> : null}
    </div>
  );
}
