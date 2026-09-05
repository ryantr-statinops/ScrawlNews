# Frontend (Web Dashboard)

> Tài liệu frontend stack, design tokens, architecture, và patterns cho web dashboard.

## Index

- [01-stack.md](01-stack.md) — Tech stack + lý do chọn (React + Vite + Mantine + ApexCharts + Zustand + TanStack Router)
- [02-design-tokens.md](02-design-tokens.md) — Color palette, typography, spacing, breakpoints
- [03-architecture.md](03-architecture.md) — Folder structure, routing (TanStack Router), state management rules
- [04-patterns.md](04-patterns.md) — SSE, error handling, loading/empty states, form, chart, notification

## Stack nhanh

| Layer | Library |
|-------|---------|
| Framework | React 18 + TypeScript + Vite |
| Routing | TanStack Router |
| UI | Mantine UI v7 |
| Chart | ApexCharts |
| Server state | TanStack Query |
| UI state | Zustand |
| Form | Mantine form + Zod |
| Realtime | SSE (EventSource) |
| Icon | Lucide React |
| Theme | Light + Dark toggle |

## Reading guide

| Bạn muốn biết… | Đọc file |
|---|---|
| Stack là gì, tại sao chọn | [01-stack.md](01-stack.md) |
| Color, font, spacing | [02-design-tokens.md](02-design-tokens.md) |
| Cấu trúc thư mục `web/src/`, routing, state | [03-architecture.md](03-architecture.md) |
| SSE, form, chart, error/loading pattern | [04-patterns.md](04-patterns.md) |

Cập nhật: 2026-09-03.
