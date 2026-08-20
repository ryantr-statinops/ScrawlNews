# Architecture

Kiến trúc hệ thống ScrawlNews: Skill-based Agent pipeline.

## System Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  Scrawler   │────▶│  Synthesizer │────▶│Messenger│
│  Service    │     │  Service     │     │ Service │
└─────────────┘     └──────────────┘     └─────────┘
       │                    │                  │
       ▼                    ▼                  ▼
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│ ArticleRepo │     │ SummaryRepo  │     │Telegram │
│             │     │              │     │  Bot    │
└─────────────┘     └──────────────┘     └─────────┘
```

## Skills

| Skill | Role | Module | Technology | Status |
|-------|------|--------|-----------|--------|
| **Scrawler** | Collector | `src/services/scrawler.py` | Python + Playwright / RSS + trafilatura | Planned |
| **Synthesizer** | Summary Wrapper | `src/services/synthesizer.py` | OpenAI / LLM API | Planned |
| **Messenger** | Notifier | `src/services/messenger.py` | Telegram Bot API | Planned |

## Data Flows

```
Google News
    │
    ▼
Scrawler ──► Raw Articles (data/raw/)
    │
    ▼
Synthesizer ──► Summaries (data/processed/)
    │
    ▼
Messenger ──► Telegram Chat
```

## Data Model

### Article
| Field | Type | Description |
|-------|------|-------------|
| `id` | TEXT (PK) | UUID hoặc SHA256 hash của URL |
| `url` | TEXT (UNIQUE) | Link gốc của bài viết |
| `title` | TEXT | Tiêu đề |
| `source` | TEXT | Nguồn tin |
| `raw_html` | TEXT | HTML gốc (optional, để re-summarize) |
| `content` | TEXT | Nội dung đã làm sạch |
| `fetched_at` | DATETIME | Thời điểm fetch |
| `summarized` | INTEGER (0/1) | Flag đã tóm tắt chưa |

### Summary
| Field | Type | Description |
|-------|------|-------------|
| `id` | TEXT (PK) | UUID |
| `article_id` | TEXT (FK) | Tham chiếu Article.id |
| `summary_text` | TEXT | Nội dung tóm tắt |
| `model_used` | TEXT | Model LLM sử dụng (e.g. "gpt-4o-mini") |
| `created_at` | DATETIME | Thời điểm tạo |

## Services

Tất cả services kế thừa `BaseService` và implement `execute()`.

- `Scrawler.execute()`: Fetch articles từ Google News
- `Synthesizer.execute()`: Nhận articles, trả về summaries
- `Messenger.execute()`: Nhận summaries, gửi qua Telegram

## Repositories

- `ArticleRepository`: CRUD articles, dedup by URL hash, cleanup old records
- `SummaryRepository`: CRUD summaries

## Edge Cases

1. **Network failure**: Retry với exponential backoff (`src/utils/retry.py`)
2. **Empty results**: Log warning, skip summarization, notify admin
3. **Rate limiting**: Respect API rate limits với queuing
4. **Duplicate articles**: Deduplicate by URL hash
5. **HTML structure change**: Dùng flexible selectors với fallback patterns
