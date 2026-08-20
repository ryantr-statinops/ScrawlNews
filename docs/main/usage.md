# Usage

Hướng dẫn sử dụng ScrawlNews agent.

## Chạy thủ công

```bash
python src/main.py
```

Pipeline sẽ:
1. Fetch tin tức mới từ Google News
2. Tóm tắt bằng LLM
3. Gửi kết quả về Telegram

## Chạy tự động

Agent được cấu hình chạy tự động qua GitHub Actions với cron:

- 08:00 UTC
- 12:00 UTC
- 16:00 UTC
- 21:00 UTC

## Dry Run

Kiểm tra pipeline không gửi Telegram:

```bash
python src/main.py --dry-run
```

## Xem lịch sử

```bash
python src/main.py --history
```

## Interactive Mode

(Nếu đã implement) Tương tác với bot để lấy chi tiết bản tin:

```bash
python src/main.py --interactive
```
