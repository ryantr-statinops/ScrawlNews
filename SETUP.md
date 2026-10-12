# Setup and first run

## Prerequisites

- Python 3.11+
- Node.js 20.19.x (`frontend/package.json` requires `>=20.19.0 <21`)
- Docker Engine with Docker Compose

## Configure

```bash
cp .env.example .env
```

Set `TELEGRAM_ENABLED=false` unless Telegram delivery is intended and both Telegram credentials are configured. The sample file defaults this setting to `true` while leaving token/chat values blank. Configure `OPENROUTER_API_KEY` or `LLM_API_KEY` before running a pipeline that needs summarization.

## Start the full local stack

```bash
docker compose up -d --build
```

- Client Product: <http://localhost:6767>
- FastAPI docs: <http://localhost:8000/docs>
- Dagster shadow UI: <http://localhost:6768>

Check status with `docker compose ps`; follow logs with `docker compose logs -f api worker beat`. Stop with `docker compose down` (without `--volumes` to preserve local data).

For Python development without Docker:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd frontend && npm ci
```

Then use `make dev` from the repository root. **It stops the current Compose stack and kills listeners on ports 8000 and 5173** before starting host processes. Read [the detailed local-development guide](docs/operations/local-development.md) first.

## Continue

- [Full documentation index](docs/README.md)
- [Configuration reference](docs/reference/configuration.md)
- [Testing and CI](docs/operations/testing.md)
- [Deployment and runtime operations](docs/operations/deployment.md)
