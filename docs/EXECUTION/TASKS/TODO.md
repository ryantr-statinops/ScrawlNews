# TODO — Những đơn vị công việc cần làm

> Các task cụ thể chưa làm / chưa chốt. Kéo từ technical debt, ideas backlog, và open questions còn lại.

## Release 1.0 hardening — High priority

- [ ] **Operational validation theo ba tầng** — dry-run; LLM thật với Telegram tắt; Telegram test chat. Ghi nhận 2–3 runs và telemetry tương ứng.
- [ ] **CI hardening** — dùng `npm ci`, bỏ `|| true` theo từng gate đã verify, đo coverage baseline và chốt Docker build gate.

## Reliability-first — Medium priority

- [ ] **Metrics** — Prometheus metrics cho runs/duration/errors (Technical Debt, Low)
- [ ] **Config validation** — stricter env var validation (Technical Debt, Medium)
- [ ] **Cost Tracking chi tiết** — quy đổi token, monthly estimate, budget alert (ideas.md #6)
- [ ] **Source reliability research** — Google News RSS và trafilatura trên các nguồn tiếng Việt.
- [ ] **Multi-source** — adapter Hacker News RSS, Reddit, custom RSS (ideas.md #4)
- [ ] **Better Summarization** — structured JSON output, dedupe similar stories, entity extraction (ideas.md #7)

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
