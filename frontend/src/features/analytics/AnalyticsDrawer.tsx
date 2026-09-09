import { useQuery } from "@tanstack/react-query";
import { Anchor, Button, Drawer, Group, ScrollArea, Table, Text } from "@mantine/core";
import { ExternalLink } from "lucide-react";
import { LoadingState } from "../../components/ui/LoadingState";
import { ErrorState } from "../../components/ui/ErrorState";
import { analyticsApi } from "./api";
import type { AnalyticsFiltersState } from "./types";

export interface DrilldownSelection {
  title: string;
  kind: "articles" | "runs" | "stages" | "sources" | "llm";
  params?: Record<string, string>;
  href?: string;
  hrefLabel?: string;
}

interface Props {
  selection: DrilldownSelection | null;
  filters: AnalyticsFiltersState;
  onClose: () => void;
}

export function AnalyticsDrawer({ selection, filters, onClose }: Props) {
  const query = useQuery({
    queryKey: ["analytics", "drilldown", filters, selection],
    queryFn: () => analyticsApi.drilldown(filters, { kind: selection!.kind, ...(selection?.params ?? {}) }),
    enabled: Boolean(selection),
  });
  const records = query.data?.records ?? [];
  const columns = records.length ? Object.keys(records[0]).slice(0, 7) : [];

  return (
    <Drawer opened={Boolean(selection)} onClose={onClose} title={selection?.title} position="right" size="xl">
      {selection?.href ? (
        <Button component="a" href={selection.href} variant="light" rightSection={<ExternalLink size={15} />} mb="md">
          {selection.hrefLabel ?? "Open related records"}
        </Button>
      ) : null}
      {query.isLoading ? <LoadingState /> : null}
      {query.error ? <ErrorState message={(query.error as Error).message} /> : null}
      {!query.isLoading && !query.error && records.length === 0 ? <Text c="dimmed">No records in this period.</Text> : null}
      {records.length ? (
        <ScrollArea>
          <Table striped highlightOnHover withTableBorder>
            <Table.Thead><Table.Tr>{columns.map((column) => <Table.Th key={column}>{column.replace(/_/g, " ")}</Table.Th>)}</Table.Tr></Table.Thead>
            <Table.Tbody>
              {records.map((record, index) => (
                <Table.Tr key={String(record.id ?? `${record.run_id}-${index}`)}>
                  {columns.map((column) => (
                    <Table.Td key={column} maw={260}>
                      {column === "url" && record[column] ? <Anchor href={String(record[column])} target="_blank">Open article</Anchor> : String(record[column] ?? "—")}
                    </Table.Td>
                  ))}
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </ScrollArea>
      ) : null}
      {records.length ? <Group justify="flex-end" mt="sm"><Text size="xs" c="dimmed">Showing {records.length} records</Text></Group> : null}
    </Drawer>
  );
}
