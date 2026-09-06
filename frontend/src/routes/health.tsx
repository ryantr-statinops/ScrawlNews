import { useQuery } from "@tanstack/react-query";
import { Card, Text, Code } from "@mantine/core";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { useLogStream } from "../lib/sse";

async function fetchHealth() {
  const res = await fetch("/health");
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export function HealthPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["health"], queryFn: fetchHealth });
  const logs = useLogStream();

  return (
    <div>
      <PageHeader title="Health" description="Liveness + readiness (DB + Redis)" />
      {isLoading ? <LoadingState /> : null}
      {error ? <ErrorState message={(error as Error).message} /> : null}
      {data ? (
        <Card shadow="sm" mb="md">
          <Text>
            status: {data.status} · db: {data.db} · redis: {data.redis}
          </Text>
        </Card>
      ) : null}
      <Card shadow="sm">
        <Text fw={600} mb="xs">
          Live logs (SSE)
        </Text>
        <Code block>
          {logs.length > 0 ? logs.join("\n") : "waiting for stream..."}
        </Code>
      </Card>
    </div>
  );
}
