# Operational Validation — 2026-09-13

## Scope

Ba pipeline runs được chạy trên SQLite tạm, giới hạn 1–2 bài và `TELEGRAM_ENABLED=false`. Database production/local không bị thay đổi. Không có secret nào được ghi vào report.

## Results

| Run | External path | Result | Evidence |
|---|---|---|---|
| 1 | Google News RSS, không LLM, không Telegram | Pass | 4 articles, 4 fallback summaries, 4 digests, 5 stage events, 4 source events, 0 LLM events, `telegram_sent=0` |
| 2 | Google News RSS + OpenRouter, không Telegram | Pipeline pass; lifecycle issue found | 4 articles/summaries, 5 LLM events (4 success, 1 empty response/fallback); phát hiện async client cleanup sau khi event loop đã đóng |
| 3 | Google News RSS + OpenRouter, single category, sau fix | Pass | 1 article, 1 summary, article-summary và topic-digest LLM events đều success, 1,710 tokens, `telegram_sent=0`, không còn event-loop warning |

## Findings and fixes

- Lệnh `python src/main.py` không import được package `src` trong môi trường sạch. Makefile và scheduled smoke đã chuyển sang `python -m src.main`.
- `fetch_limit` có thể bị vượt khi limit nhỏ hơn số category/source. Kết quả merge hiện được cap theo total limit.
- LLM async clients hiện được close trong cùng event loop đã tạo chúng.
- Mẫu URL Google News RSS trả HTTP 200 nhưng trafilatura không extract được full content; fallback title vẫn giúp pipeline hoàn thành. Cần theo dõi thêm trong source reliability research.

## Remaining validation

Telegram delivery chưa thể chạy vì local environment không có `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`. Chỉ thực hiện bước này với test chat credentials; không tự động gửi vào production chat.
