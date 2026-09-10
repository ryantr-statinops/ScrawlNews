import { Table, Badge } from "@mantine/core";
import type { Article } from "../../types/api";

export function FeedTable({ articles, onSelect }: { articles: Article[]; onSelect?: (article: Article) => void }) {
  return (
    <Table.ScrollContainer minWidth={640}>
    <Table striped highlightOnHover verticalSpacing="sm">
      <Table.Thead>
          <Table.Tr>
            <Table.Th style={{ minWidth: 280 }}>Title</Table.Th>
            <Table.Th style={{ width: 130 }}>Source</Table.Th>
            <Table.Th style={{ width: 180 }}>Fetched</Table.Th>
            <Table.Th style={{ width: 110 }}>Status</Table.Th>
          </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {articles.map((a) => (
          <Table.Tr key={a.id} onClick={() => onSelect?.(a)} style={{ cursor: onSelect ? "pointer" : undefined }}>
            <Table.Td>
              {a.title}
            </Table.Td>
            <Table.Td>{a.source ?? "-"}</Table.Td>
            <Table.Td>{a.fetched_at ? new Date(a.fetched_at).toLocaleString() : "-"}</Table.Td>
            <Table.Td>
              <Badge color={a.summarized ? "green" : "yellow"}>
                {a.summarized ? "summarized" : "pending"}
              </Badge>
            </Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
    </Table.ScrollContainer>
  );
}
