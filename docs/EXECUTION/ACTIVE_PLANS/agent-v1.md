# Agent v1 — Local Pipeline Operator

## Goal

Thêm một agent điều phối local cho ScrawlNews theo chu trình:

`Observe → Decide → Act → Verify → Record`

Agent v1 ưu tiên deterministic rules. LLM chỉ được bổ sung ở lớp diễn giải ngôn ngữ về sau, không được tự quyết định action ngoài policy.

## Scope

- Observe: đọc health, pipeline runs gần nhất và cấu hình runtime.
- Decide: tạo một `Decision` có lý do, mức rủi ro và action được policy cho phép.
- Act: hỗ trợ các action an toàn: trigger pipeline dry-run và yêu cầu backup.
- Verify: kiểm tra kết quả action qua health/run state.
- Record: ghi audit event vào SQLite với correlation id.

## Safety rules

- Mặc định `dry_run=true`.
- Không tự gửi Telegram, xoá dữ liệu hoặc thay đổi secrets.
- Action ngoài allowlist bị từ chối trước khi thực thi.
- Mỗi decision/action/verification phải có audit record.
- Nếu health không đạt hoặc policy không chắc chắn, agent chuyển sang `blocked` và yêu cầu người dùng.

## Delivery stages

1. Core contracts và rule-based policy (pure Python, không side effect).
2. Audit repository + migration.
3. Executor có dry-run và verify.
4. API endpoint + dashboard status.
5. Test integration và tài liệu vận hành.

## Acceptance criteria

- Có thể chạy agent ở local mà không cần LLM/API key.
- Unit test chứng minh action bị chặn ngoài policy.
- Dry-run không tạo pipeline task và không gửi Telegram.
- Mỗi lần chạy có audit trail truy vấn được.
- Health failure không dẫn tới action tự động.
