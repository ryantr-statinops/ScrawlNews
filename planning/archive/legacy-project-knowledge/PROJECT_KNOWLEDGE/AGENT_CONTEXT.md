# ScrawlNews — Agent Context

> Compact project context for agents and contributors. This file describes stable
> runtime contracts; verify volatile status with Git, Docker and tests.
>
> Last reviewed: 2026-09-15.

## Project purpose

ScrawlNews is a local news-reading product. It collects articles from Google News
RSS and custom RSS/Atom sources, extracts content, creates summaries and topic
digests, and optionally delivers digests through Telegram.

The product has two separate surfaces:

- Client Product: user-facing feed, search, digests, Telegram, preferences,
  insights and Assistant UX.
- Operations: internal execution visibility, asset graph, runs, logs, retries,
  failures and orchestration metadata.

## Runtime topology

| Surface | Address | Owner | Scope |
|---|---|---|---|
| Client Product | http://localhost:6767 | React/Vite through Nginx | Feed, digests, Telegram, settings, insights |
| Dagster Operations | http://localhost:6768 | Dagster webserver | Assets, runs, logs, retries and shadow metadata |
| API | http://localhost:8000 | FastAPI | Shared domain API and health endpoints |

The Client must not expose run IDs, worker details, retry internals, raw logs, stack
traces or Dagster terminology. Operations information belongs in Dagster.

## Backend and orchestration

- FastAPI exposes the domain API.
- SQLite stores domain articles, summaries, digests, configuration and telemetry.
- Redis is used by Celery.
- Celery worker executes the production pipeline.
- Celery Beat is the production scheduler and only scheduler during shadow validation.
- Dagster models six shadow assets: rss_ingestion, article_extraction,
  article_normalization, article_summarization, topic_digest_generation and
  delivery_simulation.
- Dagster shadow execution must not send Telegram, mutate production data, or
  write credentials into metadata.

## Storage ownership

| Path | Ownership | Rule |
|---|---|---|
| data/scrawlnews.db | Production domain | API/Celery data; never mutate from shadow |
| data/dagster/ | Dagster instance | Runs, events and schedule state |
| data/dagster-shadow/ | Shadow namespace | Per-run isolated outputs and comparisons |
| logs/ | Local runtime | Never commit or use as documentation source |

Shadow comparisons should verify the production database identity before and after
the run and require telegram_sent=0.

## Client boundaries

Client navigation owns the feed/article reader, search/filtering, topic digests,
Telegram preferences/status, safe settings, news insights, model analytics and
user-facing Assistant UX.

Dagster owns operational details. Do not move raw execution telemetry into the
Client merely because an API endpoint already exists. Preserve existing APIs
unless a task explicitly defines a compatible contract change.

## Configuration and security

- Credentials remain in local environment configuration during this phase.
- API responses expose configured/masked state only, never credential values.
- Never store credentials in browser storage, config history, logs, telemetry,
  reports, Dagster metadata or committed files.
- Do not print environment files or rendered compose configuration containing
  credentials.
- Non-sensitive preferences may be hot-reloaded where the API supports them.

## Testing and verification

Run focused checks first, then project gates as risk requires:

```bash
pytest -q
ruff check src/ tests/
docker-compose exec -T api mypy src/
docker-compose config
cd frontend && npm run typecheck && npm run lint && npm test -- --run
```
For runtime verification:

```bash
curl -fsS http://localhost:6767/
curl -fsS http://localhost:6768/server_info
docker-compose exec -T dagster-daemon dagster-daemon liveness-check
```

Automated tests must not call Internet, live LLM or Telegram services. Live
validation requires isolated storage, bounded input and a dedicated test chat.

## Git and change workflow

Before work:

```bash
git branch --show-current
git status --short
git log -8 --oneline
```

Do not overwrite a dirty worktree. Stage explicit paths only, inspect the staged
diff, and run git diff --cached --check before committing. Use small conventional
commits and push each completed commit to the requested remote. Never commit
environment files, databases, logs, backups, build artifacts or runtime storage.
Never force-push, amend a pushed commit, or rebase shared work without instruction.

## Source-of-truth hierarchy

Use sources in this order when they disagree:

1. Runtime code/config and observed test or Docker output.
2. CURRENT_STATE.md for implemented and verified state.
3. This file for stable agent context and boundaries.
4. TARGET_ARCHITECTURE.md for intended architecture.
5. DECISIONS.md for rationale and constraints.
6. Guides for setup, testing and deployment.
7. Changelog and archived plans for history only.

Do not treat historical documentation as current runtime truth without checking code.

## Known limitations

- Dagster is shadow-only; Celery/Beat remains production.
- Live Telegram validation requires external test credentials.
- Live LLM output is nondeterministic; parity compares lifecycle, identity, counts,
  statuses and isolation rather than exact generated text.
- Prometheus metrics, frontend coverage threshold and some source adapters are
  future work.
- SQLite is local and single-user; authentication/RBAC is not currently in scope.

## Required agent handoff

After loading this context and checking the repository, report briefly:

```text
Project purpose:
Runtime ports:
Client/Operations boundary:
Production orchestrator:
Storage:
Current branch/status:
Relevant files:
Risks/limitations:
Proposed next step:
```
