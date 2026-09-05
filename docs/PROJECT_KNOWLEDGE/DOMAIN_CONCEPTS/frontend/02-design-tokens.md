# Design Tokens

> Color, typography, spacing, breakpoints cho web dashboard. Cập nhật 2026-09-03.

## Color Palette

| Role | Light | Dark |
|------|-------|------|
| **Primary** | `#2563EB` | `#60A5FA` |
| **Accent / Signature** | `#00C7FC` | `#00C7FC` |
| **Background** | `#F8FAFC` | `#0B0F14` |
| **Surface** | `#FFFFFF` | `#121820` |
| **Text** | `#0F172A` | `#F1F5F9` |
| **Muted text** | `#64748B` | `#94A3B8` |
| **Border** | `#E2E8F0` | `#27313D` |

### Semantic colors

| Role | Light | Dark | Usage |
|------|-------|------|-------|
| `success` | `#10B981` | `#34D399` | Run success, healthy |
| `warning` | `#F59E0B` | `#FBBF24` | Pending, stale data |
| `error` | `#EF4444` | `#F87171` | Run failed, error |
| `info` | `#3B82F6` | `#60A5FA` | Neutral notification |

## Typography

| Role | Font | Weight | Size | Line height |
|------|------|--------|------|-------------|
| **Sans (UI)** | Inter | 400 | 14px | 1.5 |
| **Sans (heading)** | Inter | 600 | 24-32px | 1.2 |
| **Mono (code/data)** | JetBrains Mono | 400 | 13px | 1.5 |

### Font loading

```html
<!-- index.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

## Spacing

4-point grid (Mantine default):

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Tight gap |
| `sm` | 8px | Element gap |
| `md` | 16px | Section gap |
| `lg` | 24px | Page padding |
| `xl` | 32px | Major section |

## Breakpoints

| Token | Min width | Usage |
|-------|-----------|-------|
| `xs` | 0px | Mobile |
| `sm` | 640px | Small tablet |
| `md` | 768px | Tablet |
| `lg` | 1024px | Laptop (default) |
| `xl` | 1280px | Desktop |
| `2xl` | 1536px | Wide desktop |

## Mantine theme config

```typescript
// web/src/theme.ts
import { createTheme, MantineColorsTuple } from '@mantine/core';

const primary: MantineColorsTuple = [
  '#EFF6FF', '#DBEAFE', '#BFDBFE', '#93C5FD', '#60A5FA',
  '#3B82F6', '#2563EB', '#1D4ED8', '#1E40AF', '#1E3A8A',
];

const accent: MantineColorsTuple = [
  '#E0F7FF', '#B3EDFF', '#80E2FF', '#4DD7FF', '#26CDFF',
  '#00C7FC', '#00A6D4', '#0085AB', '#006482', '#004359',
];

export const theme = createTheme({
  primaryColor: 'primary',
  colors: { primary, accent },
  fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  fontFamilyMonospace: 'JetBrains Mono, monospace',
  defaultRadius: 'md',
  primaryShade: { light: 6, dark: 4 },
});
```

## Component tokens

| Component | Override | Value |
|-----------|----------|-------|
| Button (default) | `radius` | `md` |
| Card | `shadow` | `sm` |
| Modal | `radius` | `lg` |
| Input | `size` | `sm` (default `md`) |

## References

- [01-stack.md](01-stack.md) — UI library
- [03-architecture.md](03-architecture.md) — theme provider setup
