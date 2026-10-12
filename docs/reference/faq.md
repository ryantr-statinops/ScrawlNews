# Frequently asked questions

## How do I start the project?

Create `.env`, set `TELEGRAM_ENABLED=false` unless delivery is configured, then run `docker compose up -d --build` from the repository root. See [local development](../operations/local-development.md).

## Does the app require an LLM key just to open the dashboard?

No. A key is required when a pipeline run invokes the summarizer. `OPENROUTER_API_KEY` is preferred for the default OpenRouter provider; `LLM_API_KEY` is the fallback.

## How do I run without Telegram?

Set `TELEGRAM_ENABLED=false` in `.env`. The example file defaults it to `true` while leaving credentials blank, so override it before triggering a run if delivery is not intended.

## Is Dagster the production scheduler?

No. Celery Beat schedules production runs. Dagster is a shadow asset graph with isolated storage and simulated delivery. Its UI is at `:6768` in the full Compose stack.

## Why can a queued run be missing from the runs table briefly?

`POST /api/runs` queues a Celery task and returns a pending response. The domain run row is created when a worker starts executing it. Check `/api/tasks/{task_id}` for the Celery task state.

## Are articles and summaries automatically deleted after each run?

The current pipeline task cleans expired analytics telemetry after 30 days. It does not call article/summary cleanup helpers as part of each run. Do not manually delete SQLite files while services are using them; use [backup and recovery](../operations/backup-and-recovery.md) for database operations.

## Does the project support public hosted deployment or Reddit/Hacker News ingestion?

The checked-in runtime is local Compose plus CI/scheduled smoke; it does not include an application hosting deployment workflow. Source ingestion supports configured RSS/Atom and Google News feeds; complete Reddit and Hacker News adapters are not present.
