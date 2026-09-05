# TODO — Những đơn vị công việc cần làm

> Các task cụ thể chưa làm / chưa chốt. Kéo từ technical debt, ideas backlog, và open questions còn lại.

## High priority

- [ ] **Interactive Telegram Bot** — `/detail <id>`, `/topic tech`, `/settings` (ideas.md #1)
- [ ] **Category Filtering** — configurable categories, RSS query params, multi-feed merge (ideas.md #2)
- [ ] **Circuit breaker cho LLM API** — retry 3x đã có, thiếu circuit breaker (Technical Debt, High)
- [ ] **Monitor 2–3 GA runs** sau push, manual trigger qua dashboard `POST /api/runs` (Next Step Stage 4)

## Medium priority

- [ ] **Multi-source** — Hacker News RSS, Reddit, custom RSS (ideas.md #4)
- [ ] **Cost Tracking chi tiết** — log tokens/run, monthly estimate, budget alert (ideas.md #6)
- [ ] **Better Summarization** — structured JSON output, dedupe similar stories, entity extraction (ideas.md #7)
- [ ] **Dependency scanning** — `pip-audit` trong CI (Technical Debt, Medium)
- [ ] **Config validation** — stricter env var validation (Technical Debt, Medium)
- [ ] **Metrics** — Prometheus metrics cho runs/duration/errors (Technical Debt, Low)

## Low / Nice-to-have

- [ ] Audio Newsletter (TTS) — ideas.md #8
- [ ] Multi-language support — ideas.md #9
- [ ] Scheduled Digest Times + timezone — ideas.md #10
- [ ] Rich Formatting (MarkdownV2, inline buttons) — ideas.md #11
- [ ] Analytics & Feedback (👍/👎 learning) — ideas.md #12

## Research needed

- [ ] Google News RSS rate limits / reliability ở scale
- [ ] trafilatura quality trên Vietnamese news sites
- [ ] Playwright stealth effectiveness vs Google News
- [ ] Telegram Bot API rate limits cho broadcast
- [ ] SQLite performance với 100k+ records
- [ ] Cost optimization: batch vs per-article

## References

- [IN_PROGRESS.md](IN_PROGRESS.md) — task đang làm
- [ARCHIVED/ideas.md](../ARCHIVED/ideas.md) — backlog đầy đủ
- [COMPLETED/changelog.md](../COMPLETED/changelog.md) — technical debt tracker
