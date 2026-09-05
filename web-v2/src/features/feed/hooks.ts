import { useQuery } from "@tanstack/react-query";
import { fetchArticles } from "./api";

export function useFeedQuery(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ["articles", params],
    queryFn: () => fetchArticles(params),
  });
}
