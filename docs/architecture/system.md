# System architecture

## Runtime topology

The full Docker Compose stack contains ten services:

| Service | Role | Host endpoint / storage |
|---|---|---|
| `nginx` | Client gateway; proxies `/api` and the web UI | `http://localhost:6767` |
| `api` | FastAPI application | `http://localhost:8000`; `/docs` exposes generated API docs |
| `web` | Vite-served React Client | Container port 5173; normally reached through Nginx |
| `redis` | Celery broker and result backend | `localhost:6379` |
| `worker` | Executes `pipeline.run` tasks | No host port |
| `beat` | Schedules production Celery runs | No host port |
| `bot` | Optional Telegram polling/entrypoint process | No host port |
| `dagster-init` | Migrates the Dagster instance | No host port |
| `dagster-webserver` | Dagster shadow operations UI | `http://localhost:6768` (container port 3000) |
| `dagster-daemon` | Dagster daemon for the shadow instance | No host port |

The Compose file binds the domain database at `./data:/app/data`; the Dagster instance and shadow outputs use separate paths under that data volume. Compose reads the root `.env` file, so prepare it from `.env.example` before startup.

## Ownership boundaries

- **Client Product** is the React application served through Nginx at port 6767.
- **Operations** at port 6768 is the Dagster webserver. A separate Vite Ops router also exists in source and has its own `dev:ops` / `build:ops` commands; it is not the Dagster UI and is not the standard Compose web service.
- **FastAPI** owns domain/API behavior. The Client uses `/api` through Nginx; direct API access is available on port 8000.
- **Celery/Beat** owns production pipeline execution and scheduling.
- **Dagster** is a shadow model with isolated output paths and simulated delivery. It is not the production scheduler and its delivery asset does not send Telegram messages.
- **SQLite** is the domain store. Redis is used for Celery coordination, not as the domain database.

## Local development mode

`make dev` starts Redis and Nginx through `docker-compose.dev.yml`, then runs Uvicorn, Celery worker/Beat, the bot entrypoint, and Vite on the host. The override uses `nginx.dev.conf` to reach host processes. This mode does not start the full Dagster stack.

`make dev` is operationally invasive: the Makefile first runs `docker-compose down` and kills listeners on ports 8000 and 5173. Do not use it where those services or ports belong to another workload.

## Scheduling and external services

Celery Beat loads `schedule_times` and `schedule_timezone` from persisted config or Settings. The default is 08:00, 12:00, and 18:00 in `Asia/Ho_Chi_Minh`; `schedule_interval_hours` is a fallback only when the time list is empty. GitHub Actions runs a separate scheduled non-delivery smoke and does not deploy the application.

See [deployment and runtime operations](../operations/deployment.md) and [configuration](../reference/configuration.md).
