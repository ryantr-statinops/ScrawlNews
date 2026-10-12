# Product overview

## Purpose

ScrawlNews is a local news-monitoring dashboard. It collects articles from configured RSS/Atom sources and Google News category feeds, extracts article content, generates summaries and topic digests, and optionally sends summaries through Telegram. The dashboard is the primary user surface; collection and delivery are background pipeline capabilities.

The system is local-first and single-user. It is not a hosted multi-tenant news service, and the repository does not contain an application deployment pipeline for a public hosting platform.

## Main user workflows

1. **Monitor and filter news** — browse articles, filter by category/source/date, and open stored article content.
2. **Refresh the pipeline** — queue a Celery run, then inspect the persisted run, summaries, and digests.
3. **Manage sources and preferences** — enable or configure supported RSS sources and update runtime preferences through Settings.
4. **Review analytics** — inspect content/source/run telemetry and LLM usage/cost estimates.
5. **Use Telegram delivery optionally** — successful summaries are sent only when Telegram is enabled, credentials are available, and the run is not a dry run.
6. **Inspect operations** — use the Dagster UI for shadow asset runs; the separate Vite Ops build is partial and is not the Dagster UI.

## Implemented capabilities

- FastAPI API backed by SQLite repositories.
- Celery worker and Beat scheduler for the production pipeline.
- RSS ingestion from configured sources and Google News category feeds, concurrent fetching, and URL de-duplication.
- Article extraction, LLM summarization, category digests, and conditional Telegram delivery.
- Runtime config validation/history, telemetry-backed analytics, AI price snapshots, monthly budget estimates, and Prometheus exposition at `/metrics`.
- A React Client application and a separate, partially migrated Vite Ops application.
- Dagster shadow assets with isolated storage and simulated delivery; they do not replace Celery/Beat production scheduling.

## Boundaries and limitations

- Google News and configured RSS/Atom are supported sources. No complete Hacker News or Reddit adapter is present.
- LLM calls require a configured provider key when summarization is run; opening the dashboard does not itself require a model call.
- Telegram delivery is optional. For local operation without credentials, set `TELEGRAM_ENABLED=false`; the sample environment currently defaults it to `true`.
- Live Telegram delivery with an external test chat remains unverified. Scheduled CI smoke is non-delivery and does not establish live external-service behavior.
- Telemetry before its schema was introduced cannot be reconstructed retrospectively.
- The database is local SQLite; authentication/RBAC and multi-user operation are not implemented.

## Related references

- [System architecture](../architecture/system.md)
- [Backend and pipeline](../architecture/backend-pipeline.md)
- [Frontend](../architecture/frontend.md)
- [Configuration](../reference/configuration.md)
