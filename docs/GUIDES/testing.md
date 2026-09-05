# Guide — Testing

> Testing strategy cho ScrawlNews (BE pytest + FE Vitest), cả hai đều có theo yêu cầu.

## Test Pyramid

```
        ┌─────────────┐
        │   E2E       │  ← Few: Critical user journeys
        └─────────────┘
        ┌─────────────┐
        │ Integration │  ← Some: Service interactions
        └─────────────┘
        ┌─────────────┐
        │   Unit      │  ← Many: Individual functions/classes
        └─────────────┘
```

## Structure

```
tests/                          # BE (pytest)
├── conftest.py
├── fixtures/                   # sample_articles.json, sample_rss.xml, sample_html.html, llm_responses.json
├── unit/
│   ├── test_models.py
│   ├── test_config.py          # + hot-reload 4 vars vs secrets
│   ├── test_scrawler.py
│   ├── test_synthesizer.py
│   ├── test_messenger.py
│   ├── test_article_repo.py
│   ├── test_summary_repo.py
│   ├── test_run_repo.py
│   ├── test_api_articles.py
│   ├── test_api_runs.py        # POST /api/runs + Celery mock
│   └── test_celery_tasks.py
└── integration/
    ├── test_pipeline.py
    ├── test_database.py        # thuần local SQLite tmp
    └── test_api_integration.py

web/                             # FE (Vitest)
└── src/__tests__/
    ├── Feed.test.tsx
    ├── Summaries.test.tsx
    ├── Runs.test.tsx
    ├── Analytics.test.tsx
    └── Config.test.tsx
```

## Coverage Goals

| Component | Target |
|-----------|--------|
| Models | 100% |
| Services (core logic) | >90% |
| Repositories | >90% |
| Utils | >80% |
| Overall | >85% |

## Key Mocking Strategies

- `mock_http_client` — patch `httpx.AsyncClient` cho external calls
- `mock_openai` — patch `openai.AsyncOpenAI`
- `mock_telegram_bot` — patch `telegram.Bot`
- `temp_db` — temporary SQLite (`tmp_path`) cho test repo
- `sample_articles` — load fixture JSON

## Running Tests

```bash
# All with coverage
pytest tests/ --cov=src --cov-report=term-missing
# Unit only
pytest tests/unit/
# Integration only
pytest tests/integration/
# Specific
pytest tests/unit/test_scrawler.py::TestScrawlerService::test_fetch_rss_success -v

# FE
cd web && npm run test -- --coverage
```

## CI

```yaml
# .github/workflows/ci.yml
- pytest tests/ --cov=src --cov-fail-under=80
- cd web && npm run test -- --coverage
- mypy src/
- cd web && npm run typecheck
- ruff check src/
- cd web && npm run lint
```

## Status (2026-08-28)

- BE: 77 unit passed, 10 integration passed
- FE: 8 Vitest tests passed
- ruff passed, web lint flat (`eslint src`)

## Notes

- No real API calls trong automated tests
- Fixtures committed để reproduce
- `tests/parity/test_parity.py` (nếu có) so sánh old/new implementation

## References

- [setup.md](setup.md) — cài đặt test deps (`make install`, `make test`)
- [PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/02-core-engine.md](../PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/02-core-engine.md) — logic được test
