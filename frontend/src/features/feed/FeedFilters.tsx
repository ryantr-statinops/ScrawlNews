import { Button, Group, Select, TextInput } from "@mantine/core";

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
  return <Group mb="md">
    <TextInput placeholder="Search..." value={q} onChange={(e) => onQueryChange(e.currentTarget.value)} onKeyDown={(e) => e.key === "Enter" && onSearch()} />
    <Select placeholder="All sources" clearable data={sources} value={source} onChange={onSourceChange} />
    <Select placeholder="All categories" clearable data={categories} value={category} onChange={onCategoryChange} />
    <TextInput type="date" label="From" value={fromDate} onChange={(e) => onFromChange(e.currentTarget.value)} />
    <TextInput type="date" label="To" value={toDate} onChange={(e) => onToChange(e.currentTarget.value)} />
    <Button onClick={onSearch} loading={loading}>Search</Button>
  </Group>;
}
