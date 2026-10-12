# TODO — Những đơn vị công việc cần làm

> Các task cụ thể chưa làm / chưa chốt. Kéo từ technical debt, ideas backlog, và open questions còn lại.

## Release 1.0 hardening — Complete with exception

- [x] **Agent context gateway** — README reading contract, compact context snapshot và docs validation đã hoàn tất.

- [x] **Celery/Dagster shadow lifecycle parity** — deterministic fixture comparison, DB isolation and Telegram-disabled safety validated; see [comparison report](../COMPLETED/reports/2026-09-15-dagster-shadow-comparison.md).

- [ ] **Telegram test delivery validation (deferred)** — RSS/fallback và RSS/LLM đã pass qua 3 isolated runs; delivery với test-chat credentials chưa chạy, nhưng không phải blocker runtime khi `TELEGRAM_ENABLED=false`.

## Release 1.1 — Reliability, Security and Guardrails

- [x] **1. Frontend toolchain security** — Vite/Vitest pinned; `npm audit --audit-level=high` passes with 0 high/critical (3 moderate Vitest advisory findings remain; no `--force`).
- [x] **2. Metrics** — `/metrics` returns retained run counts, run/stage durations, and stage errors from an isolated seeded SQLite database.
- [x] **3. Config validation** — invalid multi-key updates return 400 without config/history writes; valid schedule, timezone, and range values persist atomically.
- [x] **4. Cost guardrails** — priced usage projects $25.17665 against a $0.01 budget and raises a warning-only alert; pricing is complete.
- [x] **5. Source reliability baseline** — 12 category requests, RSS 12/12 (100%, healthy), extraction 0/240 (0%, `fallback_target` in all four categories); fallback recommendation recorded.
- [x] **6. Frontend coverage** — V8 gate enforces 80% lines/statements/functions/branches; measured 99.87% / 99.87% / 84.23% / 92.20%.

Release 1.1 integration evidence: [report](../COMPLETED/reports/2026-10-04-release-1.1-integration.md).

## Release 1.2 — Source Expansion

- [ ] **Multi-source adapter contract** — canonical mapping, timeout, dedup và per-source telemetry.
- [ ] **Hacker News RSS, Reddit, custom RSS** — implement sau Release 1.1 guardrails (ideas.md #4).

## Release 1.3 — News Intelligence

- [ ] **Better Summarization** — structured JSON output, dedupe similar stories, entity extraction (ideas.md #7).
- [ ] **Analytics & Feedback** — 👍/👎 learning có audit và opt-out (ideas.md #12).

## Low / Nice-to-have

- [ ] Audio Newsletter (TTS) — ideas.md #8
- [ ] Multi-language support — ideas.md #9
- [ ] Scheduled Digest Times + timezone — ideas.md #10
- [ ] Rich Formatting (MarkdownV2, inline buttons) — ideas.md #11

## Research needed

- [ ] Playwright stealth effectiveness vs Google News
- [ ] Telegram Bot API rate limits cho broadcast
- [ ] SQLite performance với 100k+ records
- [ ] Cost optimization: batch vs per-article

## References

- [IN_PROGRESS.md](IN_PROGRESS.md) — task đang làm
- [ARCHIVED/ideas.md](../ARCHIVED/ideas.md) — backlog đầy đủ
- [COMPLETED/changelog.md](../COMPLETED/changelog.md) — technical debt tracker
