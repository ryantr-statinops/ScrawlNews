# Local development

## Prerequisites

- Python 3.11 or newer.
- Node.js 20.19.x and npm. The frontend engine range is `>=20.19.0 <21`.
- Docker Engine with Docker Compose, plus Git.

## Configure environment

```bash
cp .env.example .env
```

For a local dashboard without Telegram delivery, set `TELEGRAM_ENABLED=false` in `.env`. The sample has Telegram enabled by default while token/chat values are blank; do not leave that default if you do not intend delivery. Add an LLM key only when running a pipeline path that performs summarization.

## Full Docker Compose stack

```bash
docker compose up -d --build
```

- Client Product: <http://localhost:6767>
- FastAPI: <http://localhost:8000/docs>
- Dagster shadow UI: <http://localhost:6768>
- Redis: `localhost:6379`

Inspect with `docker compose ps` and `docker compose logs -f api worker beat`. Stop with `docker compose down`. Avoid `down --volumes` unless you intend to delete local state.

## Host-process development mode

The Makefile's `dev` target starts Redis and Nginx using the dev override, then runs Uvicorn, Celery worker/Beat, the bot entrypoint, and Vite on the host:

```bash
make dev
```

Nginx is available at `http://localhost:6767`; the direct API is on `http://localhost:8000`. This mode does not start Dagster services. **The target first runs `docker-compose down` and kills listeners on ports 8000 and 5173.** Review `Makefile` before using it on a machine with other local workloads.

For frontend-only work, from `frontend/`:

```bash
npm ci
npm run dev        # Client Vite server on :5173; /api proxies to localhost:8000
npm run dev:ops    # Partial Ops Vite app on :5174
```

The standard Ops endpoint at `:6768` is Dagster, not `dev:ops`.

## Python development environment

Prefer an isolated environment rather than installing into system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run `playwright install chromium` only if using the browser fallback. `make install` is the repository convenience target; it uses `pip --break-system-packages`, installs Playwright Chromium, then runs `npm install`. Use it only if that system-level pip behavior is acceptable in your environment.

## Useful commands

```bash
make run          # one CLI dry-run
make test         # backend suite, then frontend Vitest
make lint         # Ruff and ESLint
make typecheck    # MyPy and TypeScript
make backup
make restore BACKUP=backups/<file>.db
```

For CI's exact gates, see [testing and CI](testing.md). For configuration and runtime boundaries, see [configuration](../reference/configuration.md) and [system architecture](../architecture/system.md).
