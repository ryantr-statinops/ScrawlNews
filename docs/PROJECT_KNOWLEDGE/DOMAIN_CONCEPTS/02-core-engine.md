# 02 — Core Engine

> Bộ xử lý trung tâm. Trái tim của tool: thu thập, tóm tắt, gửi. Không chia theo tech stack.

## Flow

```
Scrawler -> dedup by SHA256 -> Synthesizer -> fallback raw -> Messenger (if enabled) -> cleanup
                Celery pipeline.run (max_retries 3)
```

## Service Interfaces

Tất cả services kế thừa `BaseService` và implement `execute()`.

```python
class BaseService(ABC):
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any: ...

class ScrawlerService(BaseService):
    async def execute(self, limit: int = 20) -> list[Article]: ...
    async def fetch_rss(self, limit: int) -> list[Article]: ...
    async def extract_content(self, url: str) -> str: ...
    async def fetch_playwright_fallback(self, limit: int) -> list[Article]: ...

class SynthesizerService(BaseService):
    async def execute(self, articles: list[Article]) -> list[Summary]: ...
    def build_prompt(self, articles: list[Article]) -> str: ...
    async def call_llm(self, prompt: str) -> str: ...
    def parse_response(self, response: str, articles: list[Article]) -> list[Summary]: ...

class MessengerService(BaseService):  # feature toggle telegram_enabled
    async def execute(self, summaries: list[Summary]) -> bool: ...
    def format_message(self, summaries: list[Summary]) -> str: ...
    def split_message(self, text: str, max_len: int = 4000) -> list[str]: ...
    async def send_messages(self, chat_id: int, messages: list[str]) -> bool: ...
```

---

## Scrawler Logic

> Logic thu thập, không gắn với feedparser hay trafilatura cụ thể.

**Responsibility**: Thu thập danh sách article từ RSS, trích xuất nội dung, deduplicate bằng `SHA256(url)[:16]`.

**Logic**:
- Fetch RSS list
- Extract content với fallback chain: Trafilatura → Readability-lxml → Playwright
- Skip article nếu extract fail, tiếp tục các article khác
- Save với dedup, đánh dấu summarized

**Implementation (Stage 2)**:
- `src/services/scrawler.py`: `fetch_rss` via httpx AsyncClient + feedparser.parse, `extract_content` via trafilatura.fetch_url/extract, SHA256(url)[:16] dedup, `fetch_playwright_fallback` stub

## Synthesizer Logic

> Logic tóm tắt, gom nhiều article vào một prompt để tiết kiệm token.

**Responsibility**: Biến danh sách article thành summaries ngắn gọn bằng LLM, có fallback.

**Logic**:
- Build prompt batch
- Call LLM
- Parse response thành summaries
- Nếu fail: trả về raw titles + URLs để vẫn có thông tin (graceful degradation)

**Implementation (Stage 2)**:
- `src/services/synthesizer.py`: AsyncOpenAI với openrouter base_url, SYSTEM_PROMPT tiếng Việt, `build_prompt` batch 500 chars, `call_llm` max_tokens 800, `parse_response` chunk, `_fallback` to titles
- Fallback khi `llm_api_key` missing

## Delivery Logic (Messenger)

> Logic gửi, là feature toggle, không phải core bắt buộc.

**Responsibility**: Gửi summaries tới Telegram nếu `telegram_enabled`, xử lý split và rate limit.

**Logic**:
- Format message, split tại `\n\n` nếu >4096 chars
- Gửi sequential 1 msg/sec
- Nếu fail: save local file, retry ở run sau
- Nếu toggle off: skip gửi, vẫn lưu summaries

**Implementation (Stage 2)**:
- `src/services/messenger.py`: check `telegram_enabled`, `format_message`, `split_message` at `\n\n` 4000, `send_messages` via python-telegram-bot Bot với `asyncio.sleep(1)`, stub fallback false
- Wired qua `src/worker/tasks.py` `pipeline_run`

---

## Implementation Notes (Stage 2–4)

- Stage 2: `src/services/base.py` abstract execute, scrawler/synthesizer/messenger wired via `pipeline.run` max_retries 3 — `9124808`
- Stage 3: messenger RetryAfter retry — `de4d045`, scrawler positional fix — `1ef51df`, summary/synthesizer fixes — `d48f6c2`..`828a9a9`
- Stage 4: legacy `src/main.py --dry-run` — `4c32b34` calls `pipeline_run` directly

## References

- [01-overview.md](01-overview.md) — core flow tổng thể
- [03-interface.md](03-interface.md) — Dashboard trigger pipeline
- [04-data-config.md](04-data-config.md) — ArticleRepo / SummaryRepo / PipelineRunRepo
- [DECISIONS.md](../DECISIONS.md) — ADR-001/002/008
- `src/services/`, `src/worker/tasks.py`
