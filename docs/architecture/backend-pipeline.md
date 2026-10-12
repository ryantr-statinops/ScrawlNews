# Backend and pipeline

## Ingestion and source selection

`ScrawlerService` reads configured source records when present; otherwise it builds feeds from configured categories and the default Google News catalog. It can fetch several feeds concurrently, records source outcomes, and de-duplicates articles by URL. Configured source URLs and Google News query feeds use the configured country/language values. This is broader than a single Google News RSS feed, but it is not a general Internet discovery system.

## Celery pipeline lifecycle

The production task is `pipeline.run` in `src/worker/tasks.py`, registered on the project Celery app. A normal task run proceeds through these stages:

1. Clean expired analytics telemetry (30-day retention); cleanup failure is logged and does not prevent the run.
2. Create a persisted `PipelineRun` with status `running` when task execution starts.
3. Fetch articles and persist new records; record source and stage telemetry.
4. Synthesize summaries and persist them; mark corresponding articles summarized.
5. Build and persist category digests.
6. If summaries exist, the run is not `dry_run`, and Telegram is enabled, send summaries through `MessengerService`.
7. Persist final run counts, delivery count, status, and finish time.

`POST /api/runs` queues a Celery task and returns a pending queue response. The domain `pipeline_runs` row is created when the worker starts the task, so a queued task can exist before its run record is visible. `/api/tasks/{task_id}` reports the Celery result state; `/api/runs/{run_id}` and `/api/runs` read domain run records.

## Retry and failure semantics

The task checkpoints article, summary, and digest IDs so a retry can resume completed work rather than re-fetching and re-saving it. It retries only retryable `ScrawlError` failures, only while below `max_retries`, and not when the task is called directly. Retry delay grows exponentially from the configured retry count. Other exceptions become failed runs; provider detail is kept in internal logs while the API receives a public error message.

Do not rely on older examples that import `src.services.exceptions` or use `@shared_task`; the current task imports errors from `src.utils.errors` and uses the configured Celery app.

## Data retention

The task explicitly cleans analytics telemetry older than 30 days. Although repositories expose article/summary cleanup helpers and Settings has `retention_days`, this task does not invoke article or summary cleanup. Do not describe those records as automatically pruned by every pipeline run without identifying another active caller.

## Celery versus Dagster

Celery/Beat remains the production pipeline and scheduler. Dagster definitions are shadow assets with per-run isolated settings/storage and Telegram disabled:

- `rss_ingestion` calls the source service.
- `article_extraction` reports how many ingested articles already have content.
- `article_normalization` filters records missing required identity fields.
- `article_summarization` and `topic_digest_generation` call the existing service layer.
- `delivery_simulation` reports counts and `telegram_sent: 0`; it does not send messages.

The asset graph models stages, but not every asset is a separate transformation engine. No production Dagster schedule is declared in the definitions module.

## Agent approval

The agent policy records a proposed action and requires explicit approval. The current approval endpoint can execute the supported database-backup action or queue a Celery dry run; it does not execute arbitrary action text. Audit events persist the decision, approval, execution, and verification results.

See [system architecture](system.md), [data and storage](data-and-storage.md), and [API reference](../reference/api.md).
