# Ideas & Future Backlog

Ý tưởng mở rộng, tính năng tương lai cho ScrawlNews.

## Priority: High (Next after Phase 1)

### 1. Interactive Telegram Bot
- User reply `/detail <id>` → bot gửi full summary + link gốc
- User reply `/topic tech` → filter chỉ tech news
- User reply `/settings` → đổi frequency, categories

### 2. Category Filtering
- Configurable categories: tech, business, world, science, sports
- RSS query params: `q=technology` hoặc `topic/technology`
- Multiple RSS feeds merge

### 3. SQLite Persistence (Phase 1 requirement)
- `articles` table: id, url, title, source, content, fetched_at, summarized
- `summaries` table: id, article_id, summary_text, model_used, created_at
- Indexes cho query nhanh
- Cleanup job: xóa records > 7 ngày

## Priority: Medium

### 4. Multi-source Support
- Hacker News RSS
- Reddit (r/technology, r/programming)
- Twitter/X lists (via Nitter RSS)
- Custom RSS feeds từ user config

### 5. Web Dashboard — Promoted to Primary Service (ADR-011 2026-08-27)
- **Now**: Local Monitor Dashboard là service chính (FastAPI + Celery + Redis + React Vite + Nginx, 1 terminal `docker compose up` / `make dev`)
- **Stack**: FastAPI + Celery Beat/Worker + Redis + React 18 TS Vite + shadcn/Tailwind + TanStack Query + Recharts + SSE
- **6 feature groups** (đã chốt full):
  1. Feed Monitor — list/search/filter articles, raw_html vs content debug
  2. Summarization Monitor — list summaries, side-by-side, token/cost, re-summarize
  3. Pipeline Control — Run Now (dry-run/real), progress, history runs, config FETCH_LIMIT trên UI, cron status
  4. Delivery Monitor — Telegram preview split 4096, toggle telegram_enabled, logs RetryAfter, fallback file
  5. System/Health — /health (DB+Redis), DB size, structured logs JSON, error board, SSE /logs/stream
  6. Analytics — chart articles/day, source dist, cost/month, feedback 👍/👎
- Legacy HTMX idea superseded by React Vite

### 6. Cost Tracking
- Log tokens used per run
- Monthly cost estimate
- Alert khi vượt budget

### 7. Better Summarization
- Structured output: JSON với fields (headline, key_points, impact, source)
- Per-article summary + daily digest
- Deduplicate similar stories (same event, different sources)
- Entity extraction: companies, people, products mentioned

## Priority: Low / Nice to Have

### 8. Audio Newsletter
- Text-to-speech (OpenAI TTS / ElevenLabs)
- Gửi file audio .ogg qua Telegram
- Playable in Telegram directly

### 9. Multi-language Support
- Detect article language
- Translate non-VN articles trước khi summarize
- Output bilingual (VN + EN)

### 10. Scheduled Digest Times
- User config gửi lúc mấy giờ
- Timezone support
- Multiple chat IDs (group + personal)

### 11. Rich Formatting
- Telegram MarkdownV2 với bold, italic, links
- Inline buttons cho "Read more", "Save", "Share"
- Image preview (nếu article có og:image)

### 12. Analytics & Feedback
- Track click-through rate (UTM params)
- User feedback: 👍 / 👎 per article
- Learning: adjust prompt based on feedback

---

## Technical Debt / Improvements

| Item | Description |
|------|-------------|
| Config system | Pydantic Settings với `.env`, validation, defaults |
| Logging | Structured logging (JSON), levels, file rotation |
| Retry policy | Exponential backoff + circuit breaker cho LLM/Telegram |
| Metrics | Prometheus metrics cho runs, duration, errors |
| CI/CD | Lint (ruff), typecheck (mypy), test trên PR |
| Dependency updates | Dependabot / Renovate config |
| Documentation | Auto-generate API docs từ code |

---

## Research Needed

- [ ] Google News RSS rate limits / reliability ở scale
- [ ] trafilatura extraction quality trên Vietnamese news sites; Readability-lxml fallback effectiveness
- [ ] Playwright stealth plugin effectiveness vs Google News
- [ ] Telegram Bot API rate limits cho broadcast
- [ ] SQLite performance với 100k+ records
- [ ] Cost optimization: batch summarization vs per-article

---

## Contribution Ideas

Nếu open source:
- Plugin system cho custom sources
- Theme-able newsletter templates
- Multi-user support (multi-tenant)
- Webhook support cho external triggers