# Roadmap

Lộ trình phát triển ScrawlNews theo 3 giai đoạn.

## Giai đoạn 1: Xây dựng Core (Local Development)

- [ ] Thiết lập môi trường Python, cài đặt Playwright và các thư viện cần thiết.
- [ ] Viết script Scrawler: Lấy tiêu đề và đường dẫn từ trang chủ Google News.
- [ ] Viết script Synthesizer: Kết nối với API LLM để nhận nội dung tóm tắt.
- [ ] Viết script Messenger: Test gửi tin nhắn qua Telegram Bot cá nhân.
- [ ] Kết nối 3 phần trên thành một pipeline chạy script đơn lẻ (`main.py`).

## Giai đoạn 2: Tối ưu & Đóng gói

- [ ] Tạo wrapper cho LLM để chuẩn hóa input/output.
- [ ] Viết file `requirements.txt` để quản lý dependencies.
- [ ] Xử lý lỗi (Error Handling): Đảm bảo bot không "chết" khi trang web thay đổi cấu trúc.
- [ ] Thêm SQLite để lưu lịch sử tin tức, tránh trùng lặp.
- [ ] Viết unit tests cho từng service.

## Giai đoạn 3: Triển khai (Deployment & Automation)

- [ ] Tạo repository trên GitHub (đã hoàn thành).
- [ ] Cấu hình GitHub Secrets cho các API Key và Token (Tuyệt đối không đẩy trực tiếp vào code).
- [ ] Tạo workflow `.github/workflows/scrawlnews.yml` với Cron Job:
  ```yml
  cron: '0 8,12,16,21 * * *'
  ```
- [ ] Test chạy thử trên runner của GitHub.

## Quản lý Cấu hình (Environment Variables)

| Variable | Mô tả | Ví dụ |
|----------|--------|-------|
| `TELEGRAM_BOT_TOKEN` | Token bot từ [@BotFather](https://t.me/BotFather) | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Chat ID cá nhân hoặc channel | `-100123456789` |
| `LLM_API_KEY` | API key cho LLM provider (OpenAI, Anthropic, v.v.) | `sk-...` |

## Mục tiêu tương lai (Bonus)

- Interactive Mode: Người dùng tương tác với Bot để lấy chi tiết một bản tin cụ thể.
- Multi-source: Hỗ trợ thêm các nguồn tin khác ngoài Google News.
- Dashboard: Web UI để xem lịch sử tin tức đã gửi.
- Filter: Cho phép user filter theo category (tech, business, world).
