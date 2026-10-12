# Frontend architecture

## Stack and entrypoint

The Client is a React 18, TypeScript, Vite 7.3.6 application using Mantine, TanStack Router/Query, ApexCharts, Zustand, and shared API clients. The repository requires Node `>=20.19.0 <21`; CI pins Node 20.19.0.

`src/main.tsx` selects the Product router or Ops router using `VITE_APP=ops` or Vite mode `ops`. Both routers are assembled explicitly with `createRoute`; routes are not generated from the filesystem.

## Client Product routes

The standard router in `src/router.tsx` contains:

- `/` — news feed
- `/summaries` — summaries
- `/delivery` — Telegram delivery
- `/analytics` — insights
- `/config` — runtime configuration
- `/settings` — preferences/source settings
- `/agent` — policy-gated assistant

The Client is the web service served through Nginx on host port 6767 in the standard Compose stack.

## Vite Ops application

`src/ops-router.tsx` is a separate, partially migrated application, not the Dagster UI:

- `/runs` and `/health` render existing pages.
- `/`, `/sources`, `/telemetry`, `/failures`, and `/orchestrator` currently render migration placeholders.
- `npm run dev:ops` serves the Ops mode on port 5174; `npm run build:ops` builds it.

The full Docker Compose stack's Operations endpoint at port 6768 is the Dagster webserver. Do not document the Vite Ops build as if Compose serves it there.

## Analytics

The Client Insights page has four tabs: Overview, News insights, Sources, and AI Usage. Filters are shared through URL state and API requests. The API surface includes overview/content/pipeline/source/AI-usage and drill-down data; the exact query parameters are listed in the [API reference](../reference/api.md).

## Data access and realtime behavior

Product screens use HTTP API clients. The shared SSE helper connects to `/api/logs/stream` for log events; SSE is not the general transport for all dashboard data. Route-level API modules exist for analytics and the agent, while shared requests use `src/lib/api.ts`.

See [local development](../operations/local-development.md) for the two Vite modes and [system architecture](system.md) for the deployed route/port boundary.
