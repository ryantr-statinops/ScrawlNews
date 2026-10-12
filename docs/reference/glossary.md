# Glossary

| Term | Meaning in ScrawlNews |
|---|---|
| Article | A source item stored in the domain SQLite database, including source, URL, category, timestamps, and extracted content when available. |
| Source | A configured RSS/Atom endpoint or built-in Google News feed definition used by the Scrawler. |
| Scrawler | Service that selects feeds, fetches articles, records per-source outcomes, and de-duplicates URLs. |
| Summary | LLM-generated summary associated with an article. |
| Topic digest | Category-level digest built from articles and their summaries. |
| Pipeline run | Persisted domain record for one `pipeline.run` execution, created when the Celery worker starts the task. |
| Celery task | Queueable work item tracked by its Celery task ID; it is separate from the persisted `pipeline_runs` record. |
| Telemetry | Stage, source, and LLM events used by analytics and metrics; telemetry retention is 30 days. |
| Client Product | Main React application served through Nginx at `localhost:6767`. |
| Vite Ops app | Separate partial React router selected by Ops build mode; not the Dagster UI. |
| Dagster shadow | Isolated Dagster assets and storage used to model pipeline operations without production scheduling or Telegram delivery. |
| Celery Beat | Active production scheduler for recurring pipeline runs. |
| Shadow DB | Per-run Dagster shadow SQLite namespace, separate from the domain database. |
| Config history | Persisted old/new values for runtime-config changes, with sensitive keys filtered from reads. |
