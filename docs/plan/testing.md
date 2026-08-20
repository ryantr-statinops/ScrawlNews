# Testing

Chiến lược test cho ScrawlNews.

## Test Plan

| Layer | Type | File |
|-------|------|------|
| Models | Unit | `tests/unit/test_models.py` |
| Scrawler | Unit | `tests/unit/test_scrawler.py` |
| Synthesizer | Unit | `tests/unit/test_synthesizer.py` |
| Messenger | Unit | `tests/unit/test_messenger.py` |
| Full pipeline | Integration | `tests/integration/test_fetch_summarize_flow.py` |
| End to end | Integration | `tests/integration/test_end_to_end.py` |

## Unit Tests

- **Models**: Validate dataclass creation, serialization, defaults.
- **Scrawler**: Mock HTTP responses, test parsing logic, test fallback selectors.
- **Synthesizer**: Mock LLM API, test prompt formatting, test chunking logic.
- **Messenger**: Mock Telegram API, test message splitting, test rate limiting.

## Integration Tests

- **Pipeline flow**: Test Scrawler → Synthesizer → Messenger với in-memory mocks.
- **E2E**: Test toàn bộ flow với real-ish fixtures (không gọi API thật).

## Parity Strategy

Nếu có legacy system, `tests/parity/test_parity.py` so sánh outputs giữa old và new implementation.

## Running Tests

```bash
make test
```

Hoặc:

```bash
pytest tests/
```
