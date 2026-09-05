# 04 — Data & Configuration

> Cách dữ liệu được lưu và cấu hình được quản lý. Gom data-flow, data model, config.

## Flow

```
RSS -> Article -> dedup -> Summary -> PipelineRun -> retention 7 days
```

## Data Model

### Article Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | TEXT | PK, NOT NULL | SHA256(url)[:16] — deterministic |
| `url` | TEXT | UNIQUE, NOT NULL | Link gốc bài viết |
| `title` | TEXT | NOT NULL | Tiêu đề |
| `source` | TEXT | | Nguồn tin |
| `raw_html` | TEXT | | HTML gốc (debug/re-summarize) |
| `content` | TEXT | | Nội dung đã extract & clean |
| `fetched_at` | DATETIME | NOT NULL, DEFAULT NOW() | Thời gian fetch |
| `summarized` | INTEGER | NOT NULL, DEFAULT 0 | 0=chưa, 1=đã tóm tắt |

### Summary Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | TEXT | PK, NOT NULL | UUID v4 |
| `article_id` | TEXT | FK→Article.id, NOT NULL | Tham chiếu Article |
| `summary_text` | TEXT | NOT NULL | Nội dung tóm tắt (Markdown) |
| `model_used` | TEXT | NOT NULL | Model LLM |
| `created_at` | DATETIME | NOT NULL, DEFAULT NOW() | Thời gian tạo |

### PipelineRun Table

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | TEXT | PK, UUID v4 | Run id |
| `status` | TEXT | NOT NULL | pending\|running\|success\|failed |
| `task_id` | TEXT | | Celery task id |
| `articles_fetched` | INTEGER | | Số articles fetch được |
| `summaries_generated` | INTEGER | | Số summaries tạo |
| `telegram_sent` | INTEGER | | 0/1 |
| `error` | TEXT | | Lỗi nếu failed |
| `started_at` | DATETIME | NOT NULL | Bắt đầu |
| `finished_at` | DATETIME | | Kết thúc |

### Indexes

```sql
CREATE INDEX idx_articles_fetched_at ON articles(fetched_at DESC);
CREATE INDEX idx_articles_summarized ON articles(summarized);
CREATE INDEX idx_summaries_article_id ON summaries(article_id);
CREATE INDEX idx_runs_started_at ON pipeline_runs(started_at DESC);
```

## Repository Pattern

- `ArticleRepository`: `save` (INSERT OR IGNORE), `get_unsummarized`, `mark_summarized`, `exists` (dedup), `cleanup_old(days=7)`
- `SummaryRepository`: `save`, `get_by_article`, `get_recent`
- `PipelineRunRepository`: `create`, `get`, `list_recent`, `update_status`
- `ConfigRepository` (Stage 3): persist + audit `settings`/`config_history`, `GET /api/config/history`

## Storage

> Lưu trữ thuần local, không service ngoài.

- Tables: articles, summaries, pipeline_runs (+ settings/config_history Stage 3)
- File mount `./data:/app/data`, backup = copy file
- Không Turso/Neon ở Stage 1–4

**Implementation (Stage 1–3)**:
- Stage 1: ArticleRepository, SummaryRepository, PipelineRunRepository với sqlite3 CREATE TABLE, indexes, `data/.gitkeep`
- Stage 2: articles dedup via INSERT OR IGNORE trong `pipeline_run` task
- Stage 3: migrate v2 settings/config_history, ConfigRepository persist + audit, full CRUD repos, `cleanup_old` days 0 handling — DONE

## Configuration

`.env` → Pydantic Settings (`src/config.py`) → inject vào Services + FastAPI Depends + Celery.

### Hot Reload

**Limited (đang chọn)**: chỉ `fetch_limit`, `summary_lang`, `telegram_enabled`, `retention_days` qua `PUT /api/config` — update in-memory + ghi DB, không reconnect.

**Full complexity (không chọn)**: nếu đổi `REDIS_URL`, `DATABASE_URL`, `LLM_API_KEY` nóng → phải reconnect redis/sqlalchemy, restart Celery worker/beat, mask secrets, đồng bộ api↔worker.

**Implementation (Stage 1–2)**:
- Stage 1: Pydantic Settings `extra=ignore`, `DATABASE_URL` sqlite local, `REDIS_URL` localhost vs `redis:6379` trong docker
- Stage 2: `GET/PUT /api/config` limited 4 vars per `src/api/routes/config.py`, secrets require restart

## References

- [02-core-engine.md](02-core-engine.md) — services dùng repositories
- [03-interface.md](03-interface.md) — endpoints config
- [DECISIONS.md](../DECISIONS.md) — ADR-003/011/013
- `src/config.py`, `src/repositories/`
