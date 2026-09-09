# Local Verification Checklist

## Before starting

```bash
cp .env.example .env
# Set LLM_API_KEY. Set Telegram values only when TELEGRAM_ENABLED=true.
```

## Start the stack

```bash
docker compose config
docker compose up -d --build
docker compose ps
```

Expected services: `api`, `worker`, `beat`, `redis`, `web`, and `nginx`.

## Check endpoints

```bash
curl -fsS http://localhost/health
curl -fsS http://localhost/api/health
curl -I http://localhost/
```

Open `http://localhost` and verify the dashboard loads.

## Trigger a manual run

```bash
curl -fsS -X POST http://localhost/api/runs \
  -H 'Content-Type: application/json' \
  -d '{}'
```

Use the returned task/run identifier to inspect status in the Runs page. Check worker logs with:

```bash
docker compose logs --tail=100 worker
docker compose logs --tail=100 api
```

Stop the stack with `docker compose down` after verification.
