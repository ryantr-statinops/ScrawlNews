# News Agent Overview

## Inventory

### Skills
| Skill | Module | Technology | Status |
|-------|--------|-----------|--------|
| Scrawler | `src/services/scrawler_service.py` | Playwright | Planned |
| Synthesizer | `src/services/synthesizer_service.py` | OpenAI / LLM | Planned |
| Messenger | `src/services/messenger_service.py` | Telegram Bot API | Planned |

### Data Flows

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

### Edge Cases
1. **Network failure**: Retry with exponential backoff (see `src/utils/retry.py`).
2. **Empty results**: Log warning, skip summarization, notify admin.
3. **Rate limiting**: Respect API rate limits with queuing.
4. **Duplicate articles**: Deduplicate by URL hash.
5. **HTML structure change**: Use flexible selectors with fallback patterns.
