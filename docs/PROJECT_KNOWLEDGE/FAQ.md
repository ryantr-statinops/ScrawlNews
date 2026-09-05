# FAQ — Câu hỏi thường gặp

> Các câu hỏi thường gặp khi làm việc với ScrawlNews. Cập nhật 2026-09-04.

## Setup

### Làm sao để chạy dashboard lần đầu?

```bash
make install           # Cài deps
cp .env.example .env   # Tạo env file
make dev               # Chạy dashboard qua Nginx
# → http://localhost
```

Xem chi tiết: [docs/GUIDES/setup.md](../GUIDES/setup.md).

### `make dev` và `docker compose up` khác gì?

| | `make dev` | `docker compose up` |
|---|---|---|
| **Backend** | uvicorn native | Docker |
| **Worker/Beat** | celery native | Docker |
| **Redis** | Docker (chỉ redis) | Docker (full stack) |
| **Nginx** | Docker | Docker |
| **Hot-reload code** | ✅ Native watcher | Cần `docker compose restart` |
| **Parity prod** | ✅ Qua Nginx :80 | ✅ Qua Nginx :80 |

Cả 2 đều parity Nginx, chọn 1.

### Tôi muốn dùng model LLM khác, đổi ở đâu?

Sửa env `LLM_MODEL` trong `.env`:
```bash
LLM_PROVIDER=openrouter
LLM_MODEL=meta/llama-3-8b-instruct    # thay vì google/gemma-2-9b-it
```

Restart: `make dev` (hoặc `docker compose restart api worker`).

## Pipeline

### Tại sao article bị duplicate?

Bài viết cùng URL xuất hiện nhiều lần trong RSS. ScrawlNews dùng `SHA256(url)[:16]` làm ID, dedup qua `INSERT OR IGNORE`.

Xem [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/04-data-config.md](DOMAIN_CONCEPTS/04-data-config.md).

### Pipeline chạy bao lâu?

~30-60s cho 1 run với 20 articles. LLM call là bottleneck (~10-30s).

Xem [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/pipeline/04-performance.md](DOMAIN_CONCEPTS/pipeline/04-performance.md).

### Tôi không muốn gửi Telegram, chỉ lưu DB thôi?

Đặt `TELEGRAM_ENABLED=false` trong `.env`:
```bash
TELEGRAM_ENABLED=false
```

Messenger stage sẽ skip. Summaries vẫn lưu vào DB, xem qua dashboard.

### LLM fail liên tục, phải làm sao?

1. Check API key còn valid: `echo $OPENROUTER_API_KEY`
2. Check rate limit: switch sang model khác (free vs paid)
3. Fallback tự động: gửi raw titles nếu LLM fail
4. Xem logs: `tail -f logs/scrawlnews.log` (hoặc dashboard Logs page)

## Database

### DB nằm ở đâu?

`data/scrawlnews.db` (mount `./data:/app/data` trong Docker). Local dev: `data/` relative to project root.

### Reset DB?

```bash
rm data/scrawlnews.db
make dev   # Auto chạy migrate lại
```

### DB lớn quá, làm sao?

Tăng cleanup frequency:
```bash
RETENTION_DAYS=3  # Thay vì 7
```

Hoặc manual cleanup:
```bash
sqlite3 data/scrawlnews.db "DELETE FROM articles WHERE fetched_at < datetime('now', '-3 days');"
```

## Frontend

### Tại sao dashboard không update real-time?

Mặc định dashboard **polling 5s**. Nếu cần real-time hơn, dùng SSE (đã có sẵn cho logs).

### Đổi port 5173?

Sửa `web/vite.config.ts`:
```typescript
export default defineConfig({
  server: { port: 3000 },
});
```

Hoặc Docker: `docker-compose.yml` `web.ports`.

### Theme dark/light?

Phase 5+ — chưa implement. Xem [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/02-design-tokens.md](DOMAIN_CONCEPTS/frontend/02-design-tokens.md) cho design tokens.

## Deployment

### Deploy public được không?

Có, thêm:
1. `.htpasswd` cho Nginx HTTP Basic
2. HTTPS với Let's Encrypt
3. Cân nhắc chuyển SQLite → PostgreSQL nếu > 1 user

Xem [docs/GUIDES/deployment.md](../GUIDES/deployment.md).

### GitHub Actions không chạy?

1. Check secrets: `Settings → Secrets → Actions`
2. Check workflow: `Actions tab` xem log
3. Manual trigger: `Run workflow` button

## Troubleshooting

### Lỗi "telegram_enabled=True requires TELEGRAM_BOT_TOKEN"

→ Set `TELEGRAM_BOT_TOKEN` trong `.env` hoặc tắt `TELEGRAM_ENABLED=false`.

### Lỗi "sqlite3.OperationalError: database is locked"

→ Chỉ chạy 1 instance. Kill process khác:
```bash
pkill -f "src/main.py"
pkill -f "celery"
```

### Lỗi "ModuleNotFoundError: No module named 'src'"

→ Chạy từ root project. Hoặc:
```bash
PYTHONPATH=. python src/main.py
```

### Lỗi "externally-managed-environment" (pip)

→ Ubuntu PEP 668. Fix:
```bash
pip install --break-system-packages -r requirements.txt
```
Hoặc dùng venv.

### Docker compose không start

```bash
docker compose logs nginx   # Xem log container
docker compose ps           # Status
docker compose config       # Validate config
```

## Architecture

### Tại sao dùng Celery thay vì chạy trực tiếp?

- LLM call lâu (10-30s), không block HTTP request
- Retry tự động khi fail
- Beat schedule cho cron jobs
- Xem ADR-012

### Tại sao SQLite không PostgreSQL?

- Personal dashboard, 1 user
- Zero config, file-based
- Đủ cho thousands of records
- Xem ADR-010

### Frontend dùng gì?

React 18 + TypeScript + Vite + Mantine UI v7 + ApexCharts + Zustand + TanStack Router. Xem [docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/frontend/01-stack.md](DOMAIN_CONCEPTS/frontend/01-stack.md).

## References

- [docs/PROJECT_KNOWLEDGE/DECISIONS.md](DECISIONS.md) — ADRs
- [docs/PROJECT_KNOWLEDGE/GLOSSARY.md](GLOSSARY.md) — thuật ngữ
- [docs/GUIDES/setup.md](../GUIDES/setup.md) — setup
- [docs/GUIDES/deployment.md](../GUIDES/deployment.md) — deploy
