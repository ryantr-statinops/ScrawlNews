# Frontend Patterns

> SSE, error handling, form, loading conventions. Cập nhật 2026-09-03.

## SSE Pattern

Backend expose `/api/logs/stream` (SSE). Wrap trong helper:

```typescript
// lib/sse.ts
export interface SSESubscription {
  close: () => void;
}

export function subscribeLogs(onMessage: (line: string) => void): SSESubscription {
  const eventSource = new EventSource('/api/logs/stream');

  eventSource.onmessage = (event) => {
    onMessage(event.data);
  };

  eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    // Mantine notification
    notifications.show({
      title: 'Log stream disconnected',
      message: 'Attempting to reconnect...',
      color: 'yellow',
    });
  };

  return {
    close: () => eventSource.close(),
  };
}
```

Usage trong component:

```typescript
useEffect(() => {
  const sub = subscribeLogs((line) => {
    setLogs((prev) => [...prev, line].slice(-500)); // keep last 500
  });
  return () => sub.close();
}, []);
```

## Error Handling

### 3 layers

1. **Network errors** (fetch fail) → TanStack Query `error`
2. **API errors** (4xx/5xx with JSON body) → parse `error.message`
3. **App errors** (boundary) → ErrorBoundary component

```typescript
// Display in component
const { data, isLoading, error, refetch } = useQuery({ ... });

if (isLoading) return <LoadingState />;
if (error) return <ErrorState error={error} onRetry={refetch} />;
return <DataView data={data} />;
```

### Global error toast

```typescript
// lib/api.ts (extend existing)
async function fetchJSON<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    notifications.show({
      title: `HTTP ${res.status}`,
      message: err.message || res.statusText,
      color: 'red',
    });
    throw new ApiError(res.status, err.message);
  }
  return res.json();
}
```

## Loading States

### 3 levels

1. **Initial load** (no cached data) → `<LoadingState />` với spinner
2. **Refetch** (có cached data) → table rows mờ đi + small spinner ở header
3. **Mutation** (form submit, button action) → button loading + disabled

```typescript
// components/ui/LoadingState.tsx
<Center h={400}>
  <Stack align="center" gap="md">
    <Loader />
    <Text c="dimmed">Loading...</Text>
  </Stack>
</Center>
```

## Empty States

```typescript
// components/ui/EmptyState.tsx
<Stack align="center" py="xl" gap="sm">
  <IconInbox size={48} stroke={1.5} color="var(--mantine-color-dimmed)" />
  <Title order={4}>No articles yet</Title>
  <Text c="dimmed" size="sm">Run pipeline to fetch news</Text>
  <Button onClick={onRun} leftSection={<IconPlay size={16} />}>Run Now</Button>
</Stack>
```

## Form Pattern

```typescript
import { useForm, zodResolver } from '@mantine/form';
import { z } from 'zod';

const schema = z.object({
  fetch_limit: z.number().min(1).max(100),
  summary_lang: z.string().min(2).max(5),
  telegram_enabled: z.boolean(),
});

export function ConfigForm() {
  const form = useForm({
    initialValues: { fetch_limit: 20, summary_lang: 'vi', telegram_enabled: true },
    validate: zodResolver(schema),
  });

  const mutation = useMutation({
    mutationFn: (values: typeof form.values) => updateConfig(values),
    onSuccess: () => notifications.show({ message: 'Config updated', color: 'green' }),
    onError: (err) => notifications.show({ message: err.message, color: 'red' }),
  });

  return (
    <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
      <NumberInput label="Fetch limit" {...form.getInputProps('fetch_limit')} />
      <TextInput label="Summary language" {...form.getInputProps('summary_lang')} />
      <Switch label="Telegram enabled" {...form.getInputProps('telegram_enabled', { type: 'checkbox' })} />
      <Button type="submit" loading={mutation.isPending}>Save</Button>
    </form>
  );
}
```

## Chart Pattern (ApexCharts)

```typescript
// components/charts/LineChart.tsx
import Chart from 'react-apexcharts';
import { useMantineTheme } from '@mantine/core';

interface Props {
  data: Array<{ x: string; y: number }>;
  height?: number;
}

export function LineChart({ data, height = 300 }: Props) {
  const theme = useMantineTheme();
  const isDark = theme.colorScheme === 'dark';

  return (
    <Chart
      type="line"
      height={height}
      options={{
        theme: { mode: isDark ? 'dark' : 'light' },
        chart: { background: 'transparent' },
        xaxis: { type: 'datetime' },
        colors: [theme.colors.primary[6]],
        grid: { borderColor: isDark ? theme.colors.dark[5] : theme.colors.gray[2] },
      }}
      series={[{ name: 'Articles', data }]}
    />
  );
}
```

## Realtime Update Pattern

Combine TanStack Query refetch + SSE:

```typescript
function useLiveRuns() {
  const query = useQuery({
    queryKey: ['runs'],
    queryFn: fetchRuns,
    refetchInterval: 5000, // fallback polling
  });

  useEffect(() => {
    // SSE for instant update
    const sub = subscribeLogs((line) => {
      if (line.includes('Run completed')) {
        query.refetch();
      }
    });
    return () => sub.close();
  }, [query]);

  return query;
}
```

## Notification Pattern

```typescript
import { notifications } from '@mantine/notifications';

// Success
notifications.show({
  title: 'Pipeline started',
  message: `Run ${runId} queued`,
  color: 'green',
  icon: <IconCheck size={16} />,
});

// Error
notifications.show({
  title: 'Pipeline failed',
  message: error.message,
  color: 'red',
  icon: <IconX size={16} />,
  autoClose: false, // require manual close for errors
});

// Info
notifications.show({
  message: 'Refreshing data...',
  color: 'blue',
  loading: true,
  withCloseButton: false,
});
```

## References

- [01-stack.md](01-stack.md) — libraries
- [02-design-tokens.md](02-design-tokens.md) — colors
- [03-architecture.md](03-architecture.md) — folder structure
