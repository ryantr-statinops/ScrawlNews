# Validation & Test Strategy

## Test Plan

| Layer | Type | File |
|-------|------|------|
| Models | Unit | `tests/unit/test_models.py` |
| Scrawler | Unit | `tests/unit/test_scrawler_service.py` |
| Synthesizer | Unit | `tests/unit/test_synthesizer_service.py` |
| Messenger | Unit | `tests/unit/test_messenger_service.py` |
| Full pipeline | Integration | `tests/integration/test_fetch_summarize_flow.py` |
| End to end | Integration | `tests/integration/test_end_to_end.py` |

## Parity Strategy

If a legacy system exists, `tests/parity/test_parity.py` compares outputs.
