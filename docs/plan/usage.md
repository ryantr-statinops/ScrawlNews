# Usage

Hướng dẫn sử dụng ScrawlNews agent.

## Chạy Thủ Công

### Chạy bình thường (gửi Telegram)

```bash
python src/main.py
```

### Dry Run (không gửi Telegram, log ra console)

```bash
python src/main.py --dry-run
```

Output mẫu:
```
[INFO] Starting ScrawlNews pipeline...
[INFO] Fetching articles from Google News RSS...
[INFO] Fetched 20 articles
[INFO] Filtering new articles...
[INFO] 15 new articles to summarize
[INFO] Summarizing with gpt-4o-mini...
[INFO] Generated 15 summaries
[INFO] Formatting newsletter...
[INFO] DRY RUN: Would send 2 messages to Telegram
[INFO] Pipeline completed in 12.3s
```

### Xem Lịch Sử

```bash
python src/main.py --history
```

Output:
```
=== ScrawlNews History ===
Total articles: 1,247
Total summaries: 1,189
Last run: 2024-01-15 21:00:00 UTC
Last newsletter sent: 2024-01-15 21:00:05 UTC

Recent runs:
  2024-01-15 21:00:00  15 articles  15 summaries  ✓ sent
  2024-01-15 16:00:00  18 articles  17 summaries  ✓ sent
  2024-01-15 12:00:00  12 articles  12 summaries  ✓ sent
  2024-01-15 08:00:00  20 articles  19 summaries  ✓ sent
```

### Debug Mode

```bash
LOG_LEVEL=DEBUG python src/main.py
```

### Chỉ Fetch (không summarize, không gửi)

```bash
python src/main.py --fetch-only
```

### Chỉ Summarize (dùng articles đã có trong DB)

```bash
python src/main.py --summarize-only
```

### Chỉ Gửi (dùng summaries đã có trong DB)

```bash
python src/main.py --send-only
```

---

## Chạy Tự Động (GitHub Actions)

Sau khi setup GitHub Secrets, workflow chạy tự động:

| Cron (UTC) | Vietnam Time (UTC+7) |
|------------|---------------------|
| 0 8 * * *  | 15:00 (3 PM)        |
| 0 12 * * * | 19:00 (7 PM)        |
| 0 16 * * * | 23:00 (11 PM)       |
| 0 21 * * * | 04:00 (4 AM next day) |

### Manual Trigger

Vào GitHub repo → Actions → ScrawlNews Daily → **Run workflow** → Chọn branch → **Run workflow**.

### Xem Logs

GitHub → Actions → Chọn workflow run → Xem logs từng step.

### Artifacts

Mỗi run tạo artifacts:
- `newsletter-<timestamp>.md` — nội dung newsletter
- `pipeline-log-<timestamp>.txt` — full logs
- `metrics-<timestamp>.json` — stats (articles, tokens, duration)

---

## Newsletter Format

Newsletter gửi về Telegram có dạng:

```
📰 **Daily News Briefing** — 2024-01-15 21:00 UTC

🔴 **AI Breakthrough: New Model Beats GPT-4**
Researchers at Stanford developed a new architecture...
[Đọc thêm](https://techcrunch.com/...)

🟢 **Vietnam Tech Startup Raises $50M Series B**
Local fintech company expands to Southeast Asia...
[Đọc thêm](https://vnexpress.net/...)

🔵 **Google Launches Gemini 2.0**
Multimodal capabilities improved significantly...
[Đọc thêm](https://blog.google/...)

---
📊 15 articles • 3.2k tokens • $0.0012 • 12.3s
```

### Message Splitting

Nếu newsletter > 4096 chars, tự động chia thành multiple messages:
- Part 1: Header + first N stories
- Part 2: Remaining stories + footer
- Mỗi part cách nhau 1 giây (Telegram rate limit)

---

## Telegram Bot Commands (Future - Phase 4+)

*Chưa implement, planned cho Interactive Mode*

| Command | Mô tả |
|---------|-------|
| `/start` | Welcome message, help |
| `/latest` | Gửi newsletter mới nhất |
| `/detail <id>` | Chi tiết một bài viết |
| `/topic <category>` | Filter theo category |
| `/settings` | Cấu hình preferences |
| `/history` | Xem lịch sử gần đây |
| `/help` | Hiển thị help |

---

## Monitoring & Debugging

### Kiểm Tra Health

```bash
# Kiểm tra database
sqlite3 data/scrawlnews.db "SELECT COUNT(*) FROM articles;"

# Kiểm tra recent runs
sqlite3 data/scrawlnews.db "
  SELECT fetched_at, COUNT(*) 
  FROM articles 
  GROUP BY date(fetched_at) 
  ORDER BY fetched_at DESC 
  LIMIT 10;
"
```

### Xem Logs

```bash
# Local logs
tail -f logs/scrawlnews.log

# GitHub Actions logs
# Vào Actions tab → Click vào run → Xem từng step
```

### Metrics Quan Trọng

| Metric | Target | Alert If |
|--------|--------|----------|
| Articles per run | 15-25 | < 5 hoặc > 50 |
| Summarization success rate | > 95% | < 90% |
| Telegram delivery rate | 100% | < 100% |
| Pipeline duration | < 30s | > 60s |
| LLM tokens/run | 3k-8k | > 15k |
| Estimated cost/run | < $0.01 | > $0.05 |

---

## Troubleshooting Commands

```bash
# Reset database (XÓA TOÀN BỘ DATA)
rm data/scrawlnews.db
python src/main.py  # Sẽ tạo DB mới

# Backup database
cp data/scrawlnews.db data/scrawlnews.db.backup.$(date +%Y%m%d)

# Xem articles chưa summarized
sqlite3 data/scrawlnews.db "SELECT id, title FROM articles WHERE summarized=0;"

# Xem summaries gần đây
sqlite3 data/scrawlnews.db "
  SELECT a.title, s.summary_text, s.created_at 
  FROM summaries s 
  JOIN articles a ON s.article_id = a.id 
  ORDER BY s.created_at DESC 
  LIMIT 5;
"
```

---

## Environment Variables Runtime Override

```bash
# Override cho một lần chạy
FETCH_LIMIT=10 SUMMARY_LANG=en python src/main.py

# Debug LLM prompt
DEBUG_PROMPT=1 python src/main.py --dry-run
```

---

## FAQ

**Q: Tại sao không nhận được newsletter trên Telegram?**
A: Kiểm tra:
1. `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID` đúng trong `.env`
2. Bot đã được add vào chat/channel
3. GitHub Actions secrets khớp với local `.env`
4. Xem logs GitHub Actions cho error details

**Q: Có thể chạy multiple instances cùng lúc không?**
A: Không khuyến nghị. SQLite locking có thể gây conflict. Chỉ chạy 1 instance.

**Q: Làm sao để đổi lịch chạy?**
A: Sửa cron trong `.github/workflows/scrawlnews.yml`.

**Q: Có thể dùng LLM provider khác không?**
A: Có, set `LLM_PROVIDER` và `LLM_MODEL` trong `.env`. Code hỗ trợ OpenAI-compatible APIs.

**Q: Data lưu ở đâu?**
A: SQLite file `data/scrawlnews.db`. Backup định kỳ bằng cách copy file này.

**Q: Có xóa data cũ tự động không?**
A: Có, `RETENTION_DAYS=7` (default). Articles > 7 ngày sẽ bị xóa mỗi run.