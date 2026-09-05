# Frontend Stack

> Tech stack + lý do chọn cho web dashboard (`web/`). Cập nhật 2026-09-03.

## Stack

| Layer | Library | Version | Lý do chọn |
|-------|---------|---------|------------|
| Framework | React | 18 | UI library chuẩn |
| Language | TypeScript | 5.3 | Type safety |
| Build | Vite | 5 | Dev server nhanh, HMR tức thì |
| Routing | **TanStack Router** | latest | Type-safe, code-splitting built-in |
| UI Library | **Mantine UI** | 7 | 100+ components, theme system, dark mode sẵn, accessibility |
| Chart | **ApexCharts** + `react-apexcharts` | 7 | Stream data tốt (real-time), nhiều chart types |
| Server state | TanStack Query | 5 | Cache, refetch, optimistic update |
| Global state | **Zustand** | latest | Lightweight, không boilerplate |
| Form | `@mantine/form` + Zod | latest | Validation schema |
| Icon | Lucide React | latest | Tree-shakeable, ~1000+ icon |
| Notification | `@mantine/notifications` | 7 | Toast tích hợp Mantine |
| Date picker | `@mantine/dates` | 7 | DateRangePicker, Calendar |
| Realtime | SSE (`EventSource`) | native | Server đã có `/api/logs/stream` |
| HTTP | Fetch wrapper (`web/src/lib/api.ts`) | native | Đủ dùng, không thêm deps |
| Data table | Mantine `Table` + custom | 7 | Sort/filter/pagination tự code |
| Theme | Light + Dark toggle | - | User preference, persist localStorage |

## Không dùng (cleanup)

- `recharts` — gỡ, dùng ApexCharts thay thế
- `tailwindcss` — gỡ, dùng Mantine CSS-in-JS
- `shadcn/ui` — chưa bao giờ dùng, docs cũ ghi nhầm
- Inline styles — chuyển sang Mantine `style` prop hoặc CSS Modules

## Lý do chọn ApexCharts thay Recharts

1. **Realtime fit**: `chart.updateSeries([...])` stream data mà không re-render toàn bộ
2. **Variety**: line, area, bar, pie, donut, heatmap, candlestick, radialBar
3. **Annotations**: dễ thêm markers, ranges, labels
4. **Performance**: virtualized canvas rendering, OK với 10K+ points
5. **Theme**: tích hợp sẵn với Mantine dark/light

## Lý do chọn TanStack Router thay React Router

1. **Type-safe**: params, search params đều typed
2. **File-based routing** (optional): tự sinh route tree
3. **Built-in code splitting**: route lazy load
4. **Search params API**: tốt hơn `useSearchParams` của React Router
5. **Cùng team với TanStack Query** (cùng tác giả Tanner Linsley)

## Lý do chọn Zustand thay Redux/Context

1. **Bundle**: ~1KB vs Redux ~7KB
2. **No boilerplate**: không cần actions, reducers, dispatch
3. **TypeScript**: type inference tốt
4. **Devtools**: có Redux DevTools extension support
5. **State ít**: dashboard chỉ cần lưu theme, sidebar collapsed, current user

## Realtime pattern

Dùng SSE cho log streaming (đã có backend), polling cho data updates:

```typescript
// Logs (SSE)
const eventSource = new EventSource('/api/logs/stream');

// Data updates (polling)
useQuery({
  queryKey: ['runs', 'latest'],
  queryFn: fetchLatestRun,
  refetchInterval: 5000,
});
```

## Tham khảo

- [02-design-tokens.md](02-design-tokens.md) — color, typography, spacing
- [03-architecture.md](03-architecture.md) — folder structure, routing, state rules
- [04-patterns.md](04-patterns.md) — SSE, error handling, form, loading
- [DECISIONS.md](../../DECISIONS.md) — ADR-011 (sẽ update)
