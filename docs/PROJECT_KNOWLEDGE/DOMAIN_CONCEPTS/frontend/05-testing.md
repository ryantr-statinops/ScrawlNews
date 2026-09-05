# 05 — Frontend Testing

> Vitest + React Testing Library strategy. Cập nhật 2026-09-04.

## Stack

| Tool | Version | Vai trò |
|------|---------|---------|
| Vitest | 1.2+ | Test runner (Vite-native) |
| React Testing Library | 14+ | Render + query components |
| @testing-library/jest-dom | 6+ | Custom matchers (toBeInTheDocument) |
| jsdom | 24+ | DOM environment for tests |
| @vitest/coverage-v8 | latest | Coverage report |

## Structure

```
web/src/
├── __tests__/
│   ├── Feed.test.tsx
│   ├── Summaries.test.tsx
│   ├── Runs.test.tsx
│   ├── Analytics.test.tsx
│   ├── Config.test.tsx
│   └── Health.test.tsx
├── lib/
│   └── __tests__/
│       └── api.test.ts
└── components/
    └── __tests__/
        └── Components.test.tsx
```

## Coverage Goals

| Component | Target |
|-----------|--------|
| Pages (Feed, Summaries, Runs, ...) | >80% |
| Components (shared) | >90% |
| Lib (api, formatters) | >90% |
| Stores (Zustand) | >80% |
| **Overall** | **>80%** |

## Test Patterns

### Page Component Test

```typescript
// web/src/__tests__/Feed.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MantineProvider } from '@mantine/core';
import { MemoryRouter } from 'react-router-dom';
import Feed from '../pages/Feed';

// Mock the API
vi.mock('../lib/api', () => ({
  fetchArticles: vi.fn(),
}));

import { fetchArticles } from '../lib/api';

describe('Feed', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.mocked(fetchArticles).mockResolvedValue({ count: 0, articles: [] });
  });

  it('renders empty state when no articles', async () => {
    render(
      <MantineProvider>
        <QueryClientProvider client={queryClient}>
          <MemoryRouter>
            <Feed />
          </MemoryRouter>
        </QueryClientProvider>
      </MantineProvider>
    );

    expect(await screen.findByText(/no articles/i)).toBeInTheDocument();
  });

  it('renders articles when fetched', async () => {
    vi.mocked(fetchArticles).mockResolvedValue({
      count: 2,
      articles: [
        { id: '1', title: 'Article 1', url: 'https://example.com/1' },
        { id: '2', title: 'Article 2', url: 'https://example.com/2' },
      ],
    });

    render(
      <MantineProvider>
        <QueryClientProvider client={queryClient}>
          <MemoryRouter>
            <Feed />
          </MemoryRouter>
        </QueryClientProvider>
      </MantineProvider>
    );

    expect(await screen.findByText('Article 1')).toBeInTheDocument();
    expect(screen.getByText('Article 2')).toBeInTheDocument();
  });

  it('shows error state on fetch failure', async () => {
    vi.mocked(fetchArticles).mockRejectedValue(new Error('Network error'));

    render(
      <MantineProvider>
        <QueryClientProvider client={queryClient}>
          <MemoryRouter>
            <Feed />
          </MemoryRouter>
        </QueryClientProvider>
      </MantineProvider>
    );

    expect(await screen.findByText(/error/i)).toBeInTheDocument();
  });
});
```

### API Lib Test

```typescript
// web/src/lib/__tests__/api.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchArticles, fetchRuns } from '../api';

describe('API', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('fetchArticles', () => {
    it('builds query string from params', async () => {
      vi.mocked(global.fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ count: 0, articles: [] }),
      } as Response);

      await fetchArticles({ q: 'AI', limit: 10 });

      expect(global.fetch).toHaveBeenCalledWith('/api/articles?q=AI&limit=10');
    });

    it('returns parsed JSON', async () => {
      vi.mocked(global.fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ count: 1, articles: [{ id: '1', title: 'X' }] }),
      } as Response);

      const result = await fetchArticles({});
      expect(result.count).toBe(1);
      expect(result.articles).toHaveLength(1);
    });

    it('throws on HTTP error', async () => {
      vi.mocked(global.fetch).mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      } as Response);

      await expect(fetchArticles({})).rejects.toThrow();
    });
  });
});
```

### SSE Hook Test

```typescript
// web/src/lib/__tests__/sse.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useLogsStream } from '../sse';

describe('useLogsStream', () => {
  let mockEventSource: any;

  beforeEach(() => {
    mockEventSource = {
      onmessage: null,
      onerror: null,
      close: vi.fn(),
    };
    global.EventSource = vi.fn(() => mockEventSource) as any;
  });

  it('connects to /api/logs/stream on mount', () => {
    renderHook(() => useLogsStream());

    expect(global.EventSource).toHaveBeenCalledWith('/api/logs/stream');
  });

  it('appends received messages to logs', () => {
    const { result } = renderHook(() => useLogsStream());

    act(() => {
      mockEventSource.onmessage({ data: 'log line 1' });
    });

    expect(result.current.logs).toContain('log line 1');
  });

  it('closes connection on unmount', () => {
    const { unmount } = renderHook(() => useLogsStream());
    unmount();

    expect(mockEventSource.close).toHaveBeenCalled();
  });
});
```

### Zustand Store Test

```typescript
// web/src/stores/__tests__/themeStore.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { useThemeStore } from '../themeStore';

describe('useThemeStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useThemeStore.setState({ colorScheme: 'dark' });
  });

  it('starts with default color scheme', () => {
    expect(useThemeStore.getState().colorScheme).toBe('dark');
  });

  it('toggles color scheme', () => {
    useThemeStore.getState().toggle();
    expect(useThemeStore.getState().colorScheme).toBe('light');

    useThemeStore.getState().toggle();
    expect(useThemeStore.getState().colorScheme).toBe('dark');
  });

  it('persists to localStorage', () => {
    useThemeStore.getState().set('light');
    const stored = JSON.parse(localStorage.getItem('scrawlnews-theme') || '{}');
    expect(stored.state.colorScheme).toBe('light');
  });
});
```

### Form Test (Mantine + Zod)

```typescript
// web/src/__tests__/Config.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import Config from '../pages/Config';

describe('Config form', () => {
  it('validates fetch_limit range', async () => {
    const user = userEvent.setup();
    render(<Config />);

    const input = screen.getByLabelText(/fetch limit/i);
    await user.clear(input);
    await user.type(input, '500'); // over max 100

    await user.click(screen.getByRole('button', { name: /save/i }));

    expect(await screen.findByText(/max.*100/i)).toBeInTheDocument();
  });

  it('submits valid values', async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    render(<Config onSave={onSave} />);

    await user.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => {
      expect(onSave).toHaveBeenCalledWith(
        expect.objectContaining({ fetch_limit: expect.any(Number) }),
      );
    });
  });
});
```

## Running Tests

```bash
cd web

# All tests
npm run test

# Watch mode
npm run test:watch

# With coverage
npm run test -- --coverage

# Specific test
npm run test -- Feed.test.tsx

# UI mode
npm run test:ui
```

## CI Integration

```yaml
# .github/workflows/ci.yml
- name: Run FE tests
  run: cd web && npm run test -- --coverage

- name: Lint FE
  run: cd web && npm run lint

- name: Typecheck FE
  run: cd web && npm run typecheck
```

## Best Practices

1. **Test user behavior, not implementation** — query by role, label, text
2. **Avoid testing internal state** — test what user sees
3. **Mock external APIs**, not internal modules
4. **One assertion per test** (when possible) — clearer failures
5. **Use `waitFor` for async** — never `setTimeout`
6. **Cleanup in `beforeEach`** — fresh state every test
7. **Don't test Mantine internals** — trust the library
8. **Use `screen.getByRole` over `getByTestId`** — better accessibility

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `act()` warnings | Wrap state updates in `act()` |
| `findBy*` not resolving | Use `await` + increase timeout |
| fetch not mocked | `vi.mock('...')` at top of file |
| Mantine theme not applied | Wrap in `<MantineProvider>` |
| Router context missing | Wrap in `<MemoryRouter>` |

## References

- [01-stack.md](01-stack.md) — testing libraries
- [04-patterns.md](04-patterns.md) — component patterns
- [backend/06-testing.md](../backend/06-testing.md) — backend tests
