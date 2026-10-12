# Configuration reference

Settings load from environment variables (including root `.env`) through Pydantic Settings. The values below are the defaults in `src/config.py`; Compose overrides Redis/Celery URLs to use the `redis` service. `.env.example` is a sample, not a complete schema.

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `APP_ENV` | `local` | Telegram credential validation is stricter for `prod`/`production`. |
| `LOG_LEVEL` | `INFO` | Application logging level. |
| `DATABASE_URL` | `sqlite:///data/scrawlnews.db` | Domain SQLite database. |
| `REDIS_URL` | `redis://localhost:6379/0` | Local Redis URL; Compose supplies the service hostname. |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery broker; Compose overrides it. |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Celery result backend; Compose overrides it. |
| `TELEGRAM_ENABLED` | `true` | Set `false` for local runs without Telegram credentials. `.env.example` leaves token/chat values blank while defaulting this to true. |
| `TELEGRAM_BOT_TOKEN` | unset | Required for actual Telegram delivery. |
| `TELEGRAM_CHAT_ID` | unset | Required for actual Telegram delivery. |
| `LLM_API_KEY` | empty | Fallback API key for the configured OpenAI-compatible provider. |
| `OPENROUTER_API_KEY` | unset | Preferred when `LLM_PROVIDER=openrouter`; used before `LLM_API_KEY`. |
| `LLM_PROVIDER` | `openrouter` | `openrouter` selects the OpenRouter API base URL; otherwise the OpenAI-compatible client uses its default base URL. |
| `LLM_MODEL` | `google/gemma-2-9b-it` | Model passed to the LLM client. |
| `LLM_PRICE_SNAPSHOT_JSON` | `{}` | JSON map keyed by provider/model with input/output USD per million tokens. |
| `LLM_MONTHLY_BUDGET_USD` | `0.0` | Nonnegative monthly budget used for warning-only analytics. |
| `FETCH_LIMIT` | `20` | Domain run fetch cap; validated from 1 to 100. |
| `SUMMARY_LANG` | `vi` | Summary language. |
| `RETENTION_DAYS` | `7` | Setting exposed to runtime config; do not assume every domain table is pruned by the pipeline. |
| `NEWS_CATEGORIES` | `technology,business,world,science` | Comma-separated ingestion categories. |
| `SCHEDULE_TIMES` | `08:00,12:00,18:00` | Comma-separated local run times. This takes precedence over the interval fallback. |
| `SCHEDULE_TIMEZONE` | `Asia/Ho_Chi_Minh` | Validated timezone for the configured schedule. |
| `SCHEDULE_INTERVAL_HOURS` | `24` | Fallback schedule interval used only when `SCHEDULE_TIMES` yields no entries. |
| `NEWS_COUNTRY` | `VN` | Google News locale country. |
| `NEWS_CITY` | `Hanoi` | Display/configuration city. |
| `DAGSTER_SHADOW_DB_URL` | `sqlite:///data/dagster-shadow/shadow.db` | Isolated shadow output database. |
| `DAGSTER_SHADOW_LIMIT` | `20` | Shadow fetch cap; validated from 1 to 100. |
| `DAGSTER_SHADOW_CATEGORIES` | `technology` | Comma-separated shadow categories. |

## Runtime configuration API

`PUT /api/config` accepts these 11 keys without restarting the API:

`fetch_limit`, `summary_lang`, `telegram_enabled`, `retention_days`, `news_categories`, `schedule_times`, `schedule_timezone`, `news_country`, `news_city`, `llm_price_snapshot_json`, and `llm_monthly_budget_usd`.

The route validates every supplied value before writing any setting/history rows. Invalid multi-key payloads are rejected atomically. Valid changes are persisted, recorded in config history, applied to the running Settings object, and published to the worker notification channel. `GET /api/config` reports safe values and configured flags; it never returns secret values. `GET /api/config/history` filters sensitive keys from the response.

Connection URLs, environment selection, credentials, provider, and model are not accepted by the runtime config endpoint; change them in `.env` and restart the relevant processes. Celery Beat reads persisted schedule times and timezone on its scheduler ticks.

## Credentials and delivery safety

- The dashboard/API can start without an LLM key; actual summarization calls need a usable key.
- The sample defaults `TELEGRAM_ENABLED=true` despite blank Telegram credentials. For a local dashboard without delivery, explicitly set `TELEGRAM_ENABLED=false` before running a pipeline.
- Production settings require Telegram token and chat ID when Telegram is enabled. Local settings do not enforce that requirement at startup, so an enabled local run can reach delivery without usable credentials and fail there.
- Never place real tokens or provider keys in tracked files.

See [local development](../operations/local-development.md), [API reference](api.md), and [data and storage](../architecture/data-and-storage.md).
