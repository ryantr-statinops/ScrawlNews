# API reference

FastAPI is the API source of truth. The interactive schema is available at `http://localhost:8000/docs` when the API is running. Route behavior and response models may be revised in code; this page is a route map, not a generated OpenAPI schema.

## Health and metrics

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | API/database/Redis health. Through Nginx this is exposed as `/api/health`. |
| `GET` | `/metrics` | Prometheus exposition from retained SQLite lifecycle/stage data. Excluded from generated OpenAPI by design. |
| `GET` | `/api/logs/stream` | Server-sent event stream for application logs. |

## Product and pipeline

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/articles` | List/search/filter articles. |
| `GET`, `POST` | `/api/sources` | List or create configured sources. |
| `PUT`, `DELETE` | `/api/sources/{source_id}` | Update or remove a source. |
| `POST` | `/api/sources/{source_id}/test` | Test a configured source. |
| `GET` | `/api/summaries` | List summaries. |
| `GET` | `/api/summaries/{summary_id}` | Read one summary. |
| `GET` | `/api/digests` | List topic digests. |
| `GET` | `/api/digests/{digest_id}` | Read one digest. |
| `GET` | `/api/digests/{digest_id}/articles` | Read articles associated with a digest. |
| `POST` | `/api/digests/regenerate` | Rebuild a digest for a category. |
| `GET` | `/api/runs` | List persisted pipeline runs. |
| `GET` | `/api/runs/summary` | Run summary statistics. |
| `POST` | `/api/runs` | Queue a Celery pipeline task. Response `pending` means queued; a domain run record is created when the worker starts. |
| `GET` | `/api/tasks/{task_id}` | Read Celery task result state. |
| `GET` | `/api/stats` | Legacy article statistics. |

## Configuration

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/config` | Safe configuration values and configured/not-configured flags; never returns secret values. |
| `PUT` | `/api/config` | Validate, persist, and apply the supported runtime configuration keys. Invalid multi-key payloads are rejected before writes. |
| `GET` | `/api/config/history` | Read filtered configuration change history. |

The supported update fields and restart boundary are in [configuration reference](configuration.md).

## Analytics

All routes use the `/api/analytics` prefix. Supported windows are `1h`, `4h`, `12h`, `24h`, `7d`, and `30d`.

- `GET /api/analytics/overview`
- `GET /api/analytics/content`
- `GET /api/analytics/pipeline`
- `GET /api/analytics/sources`
- `GET /api/analytics/ai-usage`
- `GET /api/analytics/drilldown`

Filter and drill-down parameters are declared on the route functions and should be read from the live FastAPI schema when integrating a client.

## Agent

All routes use the `/api/agent` prefix:

- `POST /api/agent/run` — request a policy decision and record audit events.
- `GET /api/agent/audit/{correlation_id}` — read the audit trail.
- `POST /api/agent/approve/{correlation_id}` — approve a pending supported action. Current supported execution paths are database backup and a queued Celery dry run; arbitrary action text is not executed.

## API contract maintenance

The previous hand-maintained YAML under execution plans was incomplete for the current Agent and configuration routes. Keep this route map aligned with FastAPI and use `/docs` as the field-level contract; do not label an incomplete static file as the complete API specification.
