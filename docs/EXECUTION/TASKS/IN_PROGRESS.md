# IN PROGRESS — Task đang thực hiện

> Các task hiện đang được làm. Cập nhật khi bắt đầu/buông task.

## Hiện tại (2026-08-28)

- [ ] **Monitor GitHub Actions runs** — theo dõi 2–3 lần chạy GA tự động sau push, xác nhận pipeline chạy không lỗi và Telegram nhận (nếu `telegram_enabled=true`).
  - Manual trigger test: dashboard `POST /api/runs` → xem `GET /api/tasks/{id}` và SSE `/api/logs/stream`.
  - Verify: SQLite `data/scrawlnews.db` có articles/summaries mới.

## Quy tắc

- Mỗi task mới: viết plan ngắn (dùng `EXECUTION/ARCHIVED/` không — dùng execplan-template nếu cần), implement, ghi vào [changelog.md](../COMPLETED/changelog.md).
- Khi xong: chuyển khỏi đây, cập nhật `TODO.md` (tick) và `roadmap.md` nếu thuộc stage.

## References

- [TASKS/TODO.md](TODO.md)
- [ACTIVE_PLANS/roadmap.md](../ACTIVE_PLANS/roadmap.md)
- [COMPLETED/changelog.md](../COMPLETED/changelog.md)
