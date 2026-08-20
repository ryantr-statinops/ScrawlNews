# ScrawlNews — Project Specification

ScrawlNews là một Agent tự động hóa quy trình thu thập, tóm tắt và phân phối tin tức hàng ngày từ Google News.

## 1. Kiến trúc Hệ thống (Modular Design)

Dự án được xây dựng dựa trên tư tưởng **Skill-based Agent**. Mỗi chức năng là một module độc lập:

### Skill 1: Scrawler (Collector)
- **Mục tiêu**: Thu thập dữ liệu từ Google News.
- **Công nghệ**: Python, Playwright.
- **Đầu ra**: Dữ liệu thô (Raw HTML/Text).

### Skill 2: Synthesizer (Summary Wrapper)
- **Mục tiêu**: Làm sạch dữ liệu và tóm tắt thành các ý chính.
- **Công nghệ**: Codex API / LLM Wrapper.
- **Đầu ra**: Văn bản tóm tắt tinh gọn.

### Skill 3: Messenger (Notifier)
- **Mục tiêu**: Gửi thông báo đến người dùng.
- **Công nghệ**: Telegram Bot API.
- **Đầu ra**: Tin nhắn trực quan qua Telegram.

## 2. Lộ trình phát triển (Implementation Roadmap)

### Giai đoạn 1: Xây dựng Core (Local Development)
- [ ] Thiết lập môi trường Python, cài đặt Playwright và các thư viện cần thiết.
- [ ] Viết script Scrawler: Lấy tiêu đề và đường dẫn từ trang chủ Google News.
- [ ] Viết script Synthesizer: Kết nối với API LLM để nhận nội dung tóm tắt.
- [ ] Viết script Messenger: Test gửi tin nhắn qua Telegram Bot cá nhân.
- [ ] Kết nối 3 phần trên thành một pipeline chạy script đơn lẻ (`main.py`).

### Giai đoạn 2: Tối ưu & Đóng gói
- [ ] Tạo wrapper cho Codex/LLM để chuẩn hóa input/output.
- [ ] Viết file `requirements.txt` để quản lý dependencies.
- [ ] Xử lý lỗi (Error Handling): Đảm bảo bot không "chết" khi trang web thay đổi cấu trúc.

### Giai đoạn 3: Triển khai (Deployment & Automation)
- [ ] Tạo repository trên GitHub.
- [ ] Cấu hình GitHub Secrets cho các API Key và Token (Tuyệt đối không đẩy trực tiếp vào code).
- [ ] Tạo workflow `.github/workflows/scrawlnews.yml` với Cron Job:
  ```yml
  cron: '0 8,12,16,21 * * *'
  ```
- [ ] Test chạy thử trên runner của GitHub.

## 3. Quản lý Cấu hình (Environment Variables)

- `TELEGRAM_BOT_TOKEN`: Token của bot bạn tạo trên BotFather.
- `TELEGRAM_CHAT_ID`: ID chat của bạn hoặc channel.
- `LLM_API_KEY`: API Key cho dịch vụ LLM.

## 4. Mục tiêu tương lai (Bonus)

- Thêm tính năng lưu lịch sử tin tức vào database (SQLite) để tránh trùng lặp.
- Cho phép người dùng tương tác với Bot để lấy thêm chi tiết một bản tin cụ thể (Interactive Mode).
