# 04 — Performance Dashboard

> Dashboard metrics: timing, cost, resource, scaling. Cập nhật 2026-09-04.

## Dashboard Summary

| Metric | Value | Notes |
|--------|-------|-------|
| **Avg run duration** | 30-60s | Depends on LLM response time |
| **Runs/day** | 4 (GA cron) + manual | Production: 4 |
| **Articles/run** | 20 (default `fetch_limit`) | Configurable 1-100 |
| **Cost/run (OpenRouter free)** | $0 | google/gemma-2-9b-it |
| **Cost/run (OpenAI gpt-4o-mini)** | ~$0.001-0.003 | 20 articles batch |
| **Cost/month** | $0-0.36 | 4 runs/day × 30 days |
| **DB size/month** | ~500KB-1MB | Auto cleanup at 7 days |
| **Memory (worker)** | ~50-100MB | Python + libs |
| **CPU (idle)** | <1% | Spikes during LLM call |

## Stage Timing (typical)

| Stage | Time | Bottleneck |
|-------|------|------------|
| RSS fetch | 1-3s | Google News RSS response |
| Content extraction (×20) | 5-15s | Network I/O (parallelizable) |
| LLM call | 10-30s | LLM inference + token count |
| Save to DB | <1s | SQLite local |
| Telegram send | 5-15s | Rate limit 1 msg/sec × N |
| Cleanup | <1s | DELETE query |
| **Total** | **~30-60s** | |

### Timing breakdown (visual)

```
Run start                                         End
   │                                                │
   ├─ RSS fetch (1-3s) ─┐                          │
   │                    │                          │
   ├─ Extract (5-15s) ──┤ (parallel)               │
   │                    │                          │
   ├─ LLM call (10-30s) ┴─── dominant ────┐        │
   │                                       │        │
   ├─ Save (1s)                           │        │
   │                                       │        │
   ├─ Telegram (5-15s, rate-limited) ─────┘        │
   │                                                │
   ├─ Cleanup (1s)                                  │
```

## Cost Estimate

### OpenRouter Free Models

| Model | Input $/1K | Output $/1K | 20 articles |
|-------|-----------|-------------|-------------|
| `google/gemma-2-9b-it` | $0 | $0 | $0 |
| `meta/llama-3-8b-instruct` | $0 | $0 | $0 |
| `mistralai/mistral-7b-instruct` | $0 | $0 | $0 |

**Total: $0/month** nếu dùng free models.

### OpenAI Paid (gpt-4o-mini)

| Batch size | Tokens | Cost/run | Cost/month (4/day) |
|------------|--------|----------|---------------------|
| 10 articles | ~3K | $0.0005 | $0.06 |
| 20 articles | ~6K | $0.001 | $0.12 |
| 50 articles | ~15K | $0.003 | $0.36 |

### OmniRoute (auto-fallback)

- RTK compression: giảm 20-40% tokens
- Auto route tới free providers khi có
- Average cost: ~$0.0001-0.0002 per run

## Resource Usage

### Memory

| Process | Idle | Peak |
|---------|------|------|
| FastAPI (uvicorn) | ~40MB | ~60MB |
| Celery worker | ~50MB | ~100MB (during LLM) |
| Celery beat | ~30MB | ~30MB |
| Redis | ~5MB | ~10MB |
| Nginx | ~3MB | ~5MB |
| Vite dev server | ~100MB | ~200MB |
| **Total docker-compose** | **~130MB** | **~250MB** |

### CPU

| Phase | CPU |
|-------|-----|
| Idle | <1% |
| RSS fetch | 5-10% (brief) |
| Content extraction | 10-20% (parallel) |
| LLM call (waiting) | <5% |
| Telegram send | 5% (sequential) |
| Peak (all parallel) | 30-50% |

### Disk

| Path | Size | Growth |
|------|------|--------|
| `data/scrawlnews.db` | ~500KB-1MB/month | +1MB/month |
| `logs/*.log` | ~10MB/month | +10MB/month (rotate) |
| `web/node_modules` | ~150MB | Stable |
| Docker images | ~500MB | Stable |

## Scaling Considerations

### Vertical (scale up)

| Limit | Current | Headroom |
|-------|---------|----------|
| `fetch_limit` | 20 (max 100) | 5x |
| Articles in DB | ~1000 | Cleanup 7d |
| LLM batch | ~20 | Depends on model context (gemma-2-9b-it: 8K, gpt-4o-mini: 128K) |
| SQLite file | ~1GB (before slow) | 1000x |

### Horizontal (scale out)

| Component | Multi-instance? | Note |
|-----------|-----------------|------|
| FastAPI | ✅ Yes | Stateless, behind Nginx |
| Celery worker | ✅ Yes | Multiple workers parallel |
| Celery beat | ❌ No | Only 1 beat leader |
| Redis | ✅ Yes | Master-replica |
| SQLite | ❌ No | Single file, switch to PostgreSQL |

### When to migrate off SQLite

- Concurrent writes > 10/sec
- DB size > 10GB
- Multiple app instances
- Need replication

**Migration path**: SQLite → PostgreSQL (rewrite `src/repositories/*.py` to use `psycopg` or `asyncpg`; Pydantic models unchanged).

## Monitoring (planned)

- `/api/health` — current health check
- `/api/live` / `/api/ready` — k8s probes
- `/api/stats` — chart data (articles/day, cost/month)
- `/api/runs` — recent runs with status
- Logs: JSON to stdout (via structlog), Docker captures

## Performance Tips

1. **Reduce `fetch_limit`**: 20 → 10 = 50% faster LLM call
2. **Disable Telegram** (`telegram_enabled=false`): save 5-15s per run
3. **Use free models**: OpenRouter free models = $0 cost
4. **Increase cleanup frequency**: `retention_days=3` → DB stays small
5. **Parallelize content extraction** (future): use `asyncio.gather()` for I/O

## References

- [01-overview.md](01-overview.md) — stages
- [02-sequence.md](02-sequence.md) — flow timing
- [03-data-model.md](03-data-model.md) — DB size
- [../04-data-config.md](../04-data-config.md) — config knobs
