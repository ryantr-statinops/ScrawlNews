# TODO — Những đơn vị công việc cần làm

> Các task cụ thể chưa làm / chưa chốt. Kéo từ technical debt, ideas backlog, và open questions còn lại.

## High priority

- [x] **Interactive Telegram Bot** — `/detail <id>`, `/topic tech`, `/settings` (ideas.md #1) — DONE `7b43b3f6`..`7cd3921e` (10 commits: bot app, 3 commands, dynamic beat scheduler, compose service)
- [x] **Category Filtering** — configurable categories, RSS query params, multi-feed merge (ideas.md #2) — DONE `0ae56821`..`e32485e0` (14 commits, pytest 96 passed)
- [x] **Circuit breaker cho LLM API** — retry 3x đã có, thiếu circuit breaker (Technical Debt, High) — DONE `0bdf5477`..`e297f746` (6 commits: breaker state machine, LLM + Telegram, health endpoint)
- [ ] **Monitor 2–3 local runs** sau khi cấu hình API key, manual trigger qua dashboard `POST /api/runs`.

## Local Release 1.0

- [ ] Ổn định pytest khi chạy toàn bộ suite
- [ ] Chuẩn hóa môi trường MyPy/Python 3.11
- [ ] Graceful handling khi Telegram disabled hoặc token không hợp lệ
- [ ] Backup/restore SQLite và rà soát dependency

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
