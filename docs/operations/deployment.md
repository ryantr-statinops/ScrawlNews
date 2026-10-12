# Deployment and runtime operations

## Supported deployment model

The repository currently describes and configures a local Docker Compose application. GitHub Actions provides CI and a scheduled non-delivery smoke; the workflows do not publish or deploy a hosted application. Do not describe this as a production cloud deployment.

The Compose stack and host ports are summarized in [system architecture](../architecture/system.md). Start it with a root `.env` file and:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f api worker beat
```

Client Product uses `http://localhost:6767`; Dagster shadow operations uses `http://localhost:6768`; FastAPI docs use `http://localhost:8000/docs`.

## Scheduler and delivery boundaries

Celery Beat is the active recurring scheduler. Dagster is a separately hosted shadow UI and isolated asset execution surface; production Dagster schedules are not enabled. The scheduled GitHub workflow is a non-delivery smoke and does not send Telegram messages or publish application artifacts.

Set `TELEGRAM_ENABLED=false` when credentials are absent or delivery is not intended. For external delivery validation, use a dedicated test chat and real credentials; no CI smoke can substitute for that check.

## Logs and health

```bash
docker compose ps
docker compose logs -f api worker beat bot dagster-webserver dagster-daemon
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:6767/api/health
curl -fsS http://localhost:8000/metrics
```

The API health endpoint checks domain dependencies; `/metrics` exports lifecycle/stage metrics from SQLite. Dagster health and run details are available through the Dagster UI and its service health checks in Compose.

## Updates and rollback

Keep local `.env` and `data/` outside version control. Before replacing application images or changing database schema, back up the domain SQLite database. Apply code updates with `docker compose up -d --build`; inspect service health and logs before triggering a pipeline run. Rollback procedures for Celery/Dagster behavior must preserve Celery Beat and worker as the production path and keep Dagster shadow data isolated.

See [backup and recovery](backup-and-recovery.md) before restoring data.
