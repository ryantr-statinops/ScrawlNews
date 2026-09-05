# Frontend Architecture

> Folder structure, routing, state management rules. Cập nhật 2026-09-03.

## Folder Structure

```
web/src/
├── main.tsx                 # Entry: providers (Mantine, Query, Router)
├── router.tsx               # TanStack Router config
├── theme.ts                 # Mantine theme (xem 02-design-tokens)
├── routes/                  # File-based routes
│   ├── __root.tsx           # Root layout (AppShell + Sidebar)
│   ├── index.tsx            # / (Feed)
│   ├── summaries.tsx        # /summaries
│   ├── runs.tsx             # /runs
│   ├── delivery.tsx         # /delivery
│   ├── analytics.tsx        # /analytics
│   ├── health.tsx           # /health
│   └── config.tsx           # /config
├── components/              # Shared UI components
│   ├── ui/                  # Wrappers over Mantine
│   │   ├── PageHeader.tsx
│   │   ├── DataTable.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── LoadingState.tsx
│   │   ├── ErrorState.tsx
│   │   └── EmptyState.tsx
│   ├── layout/              # AppShell, Sidebar, Topbar
│   │   ├── AppShell.tsx
│   │   ├── Sidebar.tsx
│   │ └── └── Topbar.tsx
│   └── charts/              # ApexCharts wrappers
│       ├── LineChart.tsx
│       ├── BarChart.tsx
│       └── DonutChart.tsx
├── features/                # Domain-specific
│   ├── feed/
│   │   ├── api.ts           # fetchArticles, etc.
│   │   ├── hooks.ts         # useFeedQuery
│   │   └── FeedTable.tsx
│   ├── runs/
│   │   ├── api.ts
│   │   ├── hooks.ts
│   │   └── RunTimeline.tsx
│   └── ...
├── stores/                  # Zustand stores
│   ├── themeStore.ts        # light/dark, toggle, persist localStorage
│   └── uiStore.ts           # sidebar collapsed, etc.
├── lib/                     # Generic utilities
│   ├── api.ts               # Fetch wrapper (existing)
│   ├── sse.ts               # EventSource helpers
│   └── format.ts            # date/number formatters
├── types/                   # Shared types
│   └── api.ts               # Article, Summary, PipelineRun (move from lib)
├── __tests__/               # Vitest tests
└── components/__tests__/    # Component tests
```

## Routing (TanStack Router)

```typescript
// router.tsx
import { createRouter, createRootRoute, createFileRoute } from '@tanstack/react-router';

const rootRoute = createRootRoute({
  component: AppShell,
});

const indexRoute = createFileRoute('/')({
  component: Feed,
});

const runsRoute = createFileRoute('/runs')({
  component: Runs,
  validateSearch: (search) => ({
    status: search.status as 'pending' | 'running' | 'success' | 'failed' | undefined,
  }),
});

export const router = createRouter({
  routeTree: rootRoute.addChildren([indexRoute, runsRoute, ...]),
});

// Type-safe router
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
```

## State Management Rules

### Server state (data từ API)

→ **TanStack Query** (`useQuery`, `useMutation`)

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['articles', { q, source, limit }],
  queryFn: () => fetchArticles({ q, source, limit }),
});
```

### Global UI state (theme, sidebar, user)

→ **Zustand store**

```typescript
// stores/themeStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type ColorScheme = 'light' | 'dark';

interface ThemeState {
  colorScheme: ColorScheme;
  toggle: () => void;
  set: (scheme: ColorScheme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      colorScheme: 'dark',
      toggle: () => set((s) => ({ colorScheme: s.colorScheme === 'dark' ? 'light' : 'dark' })),
      set: (colorScheme) => set({ colorScheme }),
    }),
    { name: 'scrawlnews-theme' },
  ),
);
```

### Form state

→ **Mantine form** + Zod

```typescript
const form = useForm({
  initialValues: { fetch_limit: 20, summary_lang: 'vi' },
  validate: zodResolver(z.object({
    fetch_limit: z.number().min(1).max(100),
    summary_lang: z.string().min(2).max(5),
  })),
});
```

### Local state (UI ephemeral)

→ **`useState`** (modal open, dropdown open, hover, ...)

## Provider Stack (main.tsx)

```typescript
<MantineProvider theme={theme} defaultColorScheme={useThemeStore(s => s.colorScheme)}>
  <Notifications />
  <QueryClientProvider client={queryClient}>
    <RouterProvider router={router} />
  </QueryClientProvider>
</MantineProvider>
```

Thứ tự: Mantine ngoài cùng (cung cấp theme + color scheme), Query bên trong, Router trong cùng.

## Conventions

- **Feature folder**: mỗi domain có folder riêng trong `features/`
- **API types**: define trong `features/<name>/api.ts` hoặc `types/api.ts`
- **Component file**: 1 component = 1 file, tên file trùng component
- **Export pattern**: named export (không default) trừ page components
- **Hook prefix**: `use` (e.g., `useFeedQuery`)

## References

- [01-stack.md](01-stack.md) — library versions
- [02-design-tokens.md](02-design-tokens.md) — theme config
- [04-patterns.md](04-patterns.md) — SSE, error, loading
