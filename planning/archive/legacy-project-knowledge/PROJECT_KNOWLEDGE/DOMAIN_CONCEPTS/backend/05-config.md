# 05 — Configuration

> Pydantic Settings, env vars, hot-reload, secrets. Cập nhật 2026-09-04.

## Overview

```
.env file → Pydantic Settings (config.py)
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
Services   FastAPI     Celery worker
(Depends)  (Depends)   (settings.xxx)
```

## Categories

### 1. Secrets (restart required)

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ⚠️ nếu `telegram_enabled=true` | Bot token |
| `TELEGRAM_CHAT_ID` | ⚠️ nếu `telegram_enabled=true` | Chat ID |
| `LLM_API_KEY` | ✅ | OpenAI key |
| `OPENROUTER_API_KEY` | ❌ | OpenRouter key |

### 2. Connection (restart required)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///data/scrawlnews.db` | SQLite file |
| `REDIS_URL` | `redis://localhost:6379/0` | Local |
| `REDIS_URL` (docker) | `redis://redis:6379/0` | Container |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Result backend |

### 3. Runtime (hot-reload 4 vars)

| Variable | Default | Hot-reload | Description |
|----------|---------|------------|-------------|
| `FETCH_LIMIT` | `20` | ✅ | Max articles per run |
| `SUMMARY_LANG` | `vi` | ✅ | Output language |
| `TELEGRAM_ENABLED` | `true` | ✅ | Toggle newsbot feature |
| `RETENTION_DAYS` | `7` | ✅ | Data retention |

### 4. Logging / App

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | DEBUG/INFO/WARNING/ERROR |
| `APP_ENV` | `local` | local/docker/ci |

## Pydantic Settings

```python
# src/config.py
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_env: str = "local"
    log_level: str = "INFO"

    # Database
    database_url: str = "sqlite:///data/scrawlnews.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Telegram
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_enabled: bool = True

    # LLM
    llm_api_key: str
    openrouter_api_key: str | None = None
    llm_provider: str = "openrouter"
    llm_model: str = "google/gemma-2-9b-it"

    # Pipeline
    fetch_limit: int = 20
    summary_lang: str = "vi"
    retention_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def check_telegram(self):
        if self.telegram_enabled and not self.telegram_bot_token:
            raise ValueError("telegram_enabled=True requires TELEGRAM_BOT_TOKEN")
        return self


settings = Settings()
```

## Hot-Reload (4 vars only)

### Limited (đang dùng)

Chỉ 4 vars đơn giản: `fetch_limit`, `summary_lang`, `telegram_enabled`, `retention_days`

```python
# src/api/routes/config.py
@router.put("/api/config")
def update_config(
    updates: ConfigUpdate,
    settings: Settings = Depends(get_settings),
):
    """Update hot-reload config (4 vars). Persist + audit."""
    # 1. Update in-memory settings
    for key, value in updates.model_dump(exclude_unset=True).items():
        if key not in {"fetch_limit", "summary_lang", "telegram_enabled", "retention_days"}:
            raise HTTPException(400, f"{key} requires restart")
        setattr(settings, key, value)

    # 2. Persist to DB (ConfigRepository)
    config_repo = ConfigRepository()
    config_repo.save(updates.model_dump(), user="dashboard")

    # 3. Publish to Redis pub/sub (other workers pick up)
    redis_client.publish("scrawlnews:config", json.dumps(updates.model_dump()))

    return settings
```

### Full (NOT supported)

Các vars sau yêu cầu restart vì:
- `REDIS_URL` / `DATABASE_URL` — phải reconnect engine/connection
- `LLM_API_KEY` — secret, mask trong logs
- `CELERY_*` — Celery không hỗ trợ đổi broker runtime
- `LOG_LEVEL` — yêu cầu reconfigure structlog

## Validation

```python
# src/api/routes/config.py
class ConfigUpdate(BaseModel):
    fetch_limit: int | None = Field(None, ge=1, le=100)
    summary_lang: str | None = Field(None, min_length=2, max_length=5)
    telegram_enabled: bool | None = None
    retention_days: int | None = Field(None, ge=0, le=365)
```

Pydantic validate tự động, trả 422 nếu fail.

## Config History (audit)

```python
# src/repositories/config_repo.py
class ConfigRepository:
    def save(self, config: dict, user: str) -> None:
        """Save config + audit history."""
        with self._connect() as conn:
            # 1. Upsert current settings
            for key, value in config.items():
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                    (key, str(value), datetime.utcnow()),
                )

            # 2. Insert audit log
            conn.execute(
                "INSERT INTO config_history (key, value, user, changed_at) VALUES (?, ?, ?, ?)",
                ("batch", json.dumps(config), user, datetime.utcnow()),
            )
            conn.commit()
```

`GET /api/config/history` trả lịch sử thay đổi.

## Secrets Management

### Local dev

- File `.env` (gitignored)
- Copy từ `.env.example`
- Không commit

### Production

- GitHub Secrets (cho GitHub Actions)
- Docker secrets (Swarm mode)
- Environment variables trong docker-compose
- Vault / AWS Secrets Manager (nếu scale)

### Best practices

- Không log secrets (mask trong structlog processor)
- Không return secrets qua API (filter ở Pydantic)
- Rotate tokens định kỳ
- Telegram chat ID là public info, nhưng token thì KHÔNG

## Environment Profiles

| Profile | APP_ENV | Use case |
|---------|---------|----------|
| `local` | `local` | Dev trên máy, SQLite + Redis local |
| `docker` | `docker` | Container, SQLite mount + Redis container |
| `ci` | `ci` | GitHub Actions, optional Redis |

Mỗi profile có thể có:
- `.env.local` (gitignored)
- `.env.docker` (template)
- `.env.ci` (template)

## References

- [01-stack.md](01-stack.md) — pydantic-settings
- [03-patterns.md](03-patterns.md) — ConfigError
- [04-pipeline.md](04-pipeline.md) — settings used in pipeline
- [setup.md](../../../GUIDES/setup.md) — env var reference table
