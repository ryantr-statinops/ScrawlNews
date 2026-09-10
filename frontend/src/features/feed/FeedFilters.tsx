import { Button, Card, Grid, Select, Text, TextInput } from "@mantine/core";

export function FeedFilters({
  q, source, category, sources, categories, fromDate, toDate,
  onQueryChange, onSourceChange, onCategoryChange, onFromChange, onToChange, onSearch, loading,
}: {
  q: string; source: string | null; category: string | null; sources: string[]; categories: string[];
  fromDate: string; toDate: string; onQueryChange: (value: string) => void;
  onSourceChange: (value: string | null) => void; onCategoryChange: (value: string | null) => void;
  onFromChange: (value: string) => void; onToChange: (value: string) => void;
  onSearch: () => void; loading: boolean;
}) {
  return <Card withBorder mb="md" padding="md">
    <Grid align="end" gutter="sm">
      <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}><TextInput label="Search" placeholder="Search articles..." value={q} onChange={(e) => onQueryChange(e.currentTarget.value)} onKeyDown={(e) => e.key === "Enter" && onSearch()} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6, lg: 2 }}><Select label="Source" placeholder="All sources" clearable data={sources} value={source} onChange={onSourceChange} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6, lg: 2 }}><Select label="Category" placeholder="All categories" clearable data={categories} value={category} onChange={onCategoryChange} /></Grid.Col>
      <Grid.Col span={{ base: 6, sm: 3, lg: 2 }}><TextInput type="date" label="From" value={fromDate} onChange={(e) => onFromChange(e.currentTarget.value)} /></Grid.Col>
      <Grid.Col span={{ base: 6, sm: 3, lg: 2 }}><TextInput type="date" label="To" value={toDate} onChange={(e) => onToChange(e.currentTarget.value)} /></Grid.Col>
      <Grid.Col span={{ base: 12, sm: 6, lg: 1 }}><Button fullWidth onClick={onSearch} loading={loading}>Search</Button></Grid.Col>
    </Grid>
    <Text size="xs" c="dimmed" mt="xs">Date filters use Asia/Ho_Chi_Minh time.</Text>
  </Card>;
}
