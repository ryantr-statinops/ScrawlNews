# Contributor context

## Purpose and runtime

ScrawlNews is a local-first news dashboard with an optional Celery pipeline for ingestion, summaries, digests, and Telegram delivery. The standard Compose gateway is `localhost:6767`; FastAPI is `localhost:8000`; Dagster shadow UI is `localhost:6768`; Redis is `localhost:6379`.

## Boundaries

- Celery/Beat is the production pipeline and scheduler.
- Dagster is shadow-only, uses isolated storage, and simulates delivery.
- The Client Product and Vite Ops app are separate frontend modes. Compose's `:6768` is Dagster, not Vite Ops.
- SQLite is the local domain store. Redis is Celery coordination.
- Telegram is optional; local runs without credentials should set `TELEGRAM_ENABLED=false`.

## Source-of-truth order

1. Checked-in source and runtime configuration.
2. Tests and CI definitions/results for the exact source tree.
3. The relevant current reference under this `docs/` tree.
4. Dated reports and changelog entries for historical evidence only.

Do not infer that a target-state document, roadmap, or historical verification report describes current behavior. Verify current branch, status, and recent CI before changing code.

## Useful locations

- Product behavior: [overview](../product/overview.md)
- Runtime boundaries: [system architecture](../architecture/system.md)
- Pipeline: [backend and pipeline](../architecture/backend-pipeline.md)
- Configuration/API: [configuration](../reference/configuration.md), [API](../reference/api.md)
- Local operations: [development](local-development.md), [testing](testing.md), [deployment](deployment.md)
