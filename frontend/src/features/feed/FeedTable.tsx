import { Table, Anchor, Badge } from "@mantine/core";
import type { Article } from "../../types/api";

export function FeedTable({ articles }: { articles: Article[] }) {
  return (
    <Table striped highlightOnHover>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Title</Table.Th>
          <Table.Th>Source</Table.Th>
          <Table.Th>Status</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {articles.map((a) => (
          <Table.Tr key={a.id}>
            <Table.Td>
              <Anchor href={a.url} target="_blank" rel="noreferrer">
                {a.title}
              </Anchor>
            </Table.Td>
            <Table.Td>{a.source ?? "-"}</Table.Td>
            <Table.Td>
              <Badge color={a.summarized ? "green" : "yellow"}>
                {a.summarized ? "summarized" : "pending"}
              </Badge>
            </Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
}
