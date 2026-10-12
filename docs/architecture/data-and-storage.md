# Data and storage

## Domain database

The domain application uses a local SQLite file. The default URL is `sqlite:///data/scrawlnews.db`; Compose mounts `./data` into `/app/data`. Repositories use the configured database URL and migrations are applied through `src/repositories/migrate.py` (current schema version: 9).

The domain database stores configured sources, articles, summaries, topic digests, pipeline runs, settings/config history, agent audit events, and analytics telemetry. SQLite is the application data store; Redis is not.

## Redis and Celery

Compose runs Redis separately. Celery uses Redis for its broker and result backend. This coordination state is distinct from persisted domain run records in SQLite: the API can return a queued Celery task before the worker creates the corresponding `pipeline_runs` row.

## Dagster storage isolation

Dagster's instance event storage uses `data/dagster/`. Shadow outputs use a separate per-run namespace under `data/dagster-shadow/`. The shadow settings temporarily point services at that isolated database and disable Telegram, so asset execution does not write to the domain SQLite database or send delivery messages.

## Telemetry retention

Analytics telemetry is additive and may be collected only after the relevant telemetry schema is present. The Celery task attempts to delete telemetry older than 30 days when a run starts. Earlier schema versions cannot be retroactively populated with stage/source/LLM observations.

The Settings field `retention_days` exists, but it is not the telemetry cleanup period. The current pipeline task does not call article/summary cleanup helpers; do not infer domain-data deletion solely from the existence of that setting or repository methods.

## Backups

`make backup` and `make restore BACKUP=...` use `scripts/db.py` for SQLite backup/restore. Restore first creates a safety backup and should be performed with database-writing services stopped. See [backup and recovery](../operations/backup-and-recovery.md).
