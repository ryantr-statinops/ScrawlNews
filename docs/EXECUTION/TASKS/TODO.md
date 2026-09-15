# TODO — Những đơn vị công việc cần làm

> Các task cụ thể chưa làm / chưa chốt. Kéo từ technical debt, ideas backlog, và open questions còn lại.

## Release 1.0 hardening — Complete with exception

- [x] **Agent context gateway** — README reading contract, compact context snapshot và docs validation đã hoàn tất.

- [x] **Celery/Dagster shadow lifecycle parity** — deterministic fixture comparison, DB isolation and Telegram-disabled safety validated; see [comparison report](../COMPLETED/reports/2026-09-15-dagster-shadow-comparison.md).

- [ ] **Telegram test delivery validation (deferred)** — RSS/fallback và RSS/LLM đã pass qua 3 isolated runs; delivery với test-chat credentials chưa chạy, nhưng không phải blocker runtime khi `TELEGRAM_ENABLED=false`.

## Release 1.1 — Reliability, Security and Guardrails

- [ ] **1. Frontend toolchain security** — migrate Vite/Vitest theo major versions; xử lý 2 moderate, 1 high, 1 critical audit findings mà không dùng `npm audit fix --force`.
- [ ] **2. Metrics** — Prometheus metrics cho runs/duration/errors/stage latency.
- [ ] **3. Config validation** — stricter validation cho schedule, limit, timezone, URLs và Telegram production config.
- [ ] **4. Cost guardrails** — configurable provider price snapshot, monthly estimate và budget alert (ideas.md #6).
- [ ] **5. Source reliability baseline** — Google News RSS/trafilatura trên nguồn tiếng Việt; đề xuất fallback và success-rate target.
- [ ] **6. Frontend coverage** — thêm tests cho critical routes/API states và chốt threshold từ baseline 11.12%.

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
