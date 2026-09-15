# Local Verification Checklist

## Before starting

```bash
cp .env.example .env
# Set LLM_API_KEY. Set Telegram values only when TELEGRAM_ENABLED=true.
```

## Start the stack

```bash
docker-compose config
docker-compose up -d --build
docker-compose ps
```

Expected product services: `api`, `worker`, `beat`, `bot`, `redis`, `web`, and
`nginx`. Expected Dagster Operations services: `dagster-init`,
`dagster-webserver`, and `dagster-daemon`.

## Check endpoints

```bash
curl -fsS http://localhost:6767/api/health
curl -fsS http://localhost:8000/health
curl -I http://localhost:6767/
```

The first health check goes through the Nginx gateway; the second calls FastAPI
directly. Open `http://localhost:6767` and verify the dashboard loads.

## Trigger a manual run

```bash
curl -fsS -X POST http://localhost:6767/api/runs \
  -H 'Content-Type: application/json' \
  -d '{}'
```

Use the returned task/run identifier to inspect status in the Runs page. Check worker logs with:

```bash
docker-compose logs --tail=100 worker
docker-compose logs --tail=100 api
```

Stop the stack with `docker-compose down` after verification.
