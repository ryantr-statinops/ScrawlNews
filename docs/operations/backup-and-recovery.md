# SQLite backup and recovery

## Backup

The domain database defaults to `data/scrawlnews.db`. The helper reads `DATABASE_URL` from the process environment and falls back to `sqlite:///data/scrawlnews.db`; it does not source `.env` itself. For a non-default database, export `DATABASE_URL` before invoking the Make target.

```bash
make backup
```

The helper uses SQLite's online backup API, checks the result, and writes `backups/<database-name>-<UTC timestamp>.db`. Backups contain application data and must remain local; `backups/` is gitignored.

## Restore

Stop all services that may use local state before restoring. For the standard Compose stack:

```bash
docker compose stop api worker beat bot dagster-webserver dagster-daemon
make restore BACKUP=backups/<file>.db
docker compose start api worker beat bot dagster-webserver dagster-daemon
```

The restore helper verifies the source backup, creates a safety backup of the existing target if present, restores the selected database, and verifies the restored file. By default the target is derived from the process `DATABASE_URL`; the helper supports only `sqlite:///...` URLs.

Do not copy Dagster shadow files into the domain database. Dagster instance and shadow data live in separate paths under `data/` and have different ownership.
