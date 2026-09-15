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
├── fixtures/                   # sample data + shadow_pipeline.json (deterministic)
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
│   ├── test_analytics_service.py # windows, comparison, telemetry aggregates
│   ├── test_analytics_api.py    # handler/OpenAPI contract + legacy /api/stats
│   ├── test_telemetry_repo.py   # event persistence + 30-day cleanup
│   ├── test_celery_tasks.py
│   ├── test_dagster_shadow.py
│   ├── test_dagster_fixtures.py
│   ├── test_dagster_comparison.py
│   └── test_dagster_lifecycle_parity.py
└── integration/
    ├── test_pipeline.py
    ├── test_database.py        # thuần local SQLite tmp
    └── test_api_integration.py

frontend/                         # FE (Vitest)
└── src/__tests__/
    ├── FeedTable.test.tsx
    └── AnalyticsKpi.test.tsx
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
- `shadow_pipeline.json` — fixed RSS/summary/digest values with Telegram disabled

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
cd frontend && npm run test
```

## CI

```yaml
# .github/workflows/ci.yml
- pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=85
- cd frontend && npm run test
- mypy src/
- cd frontend && npm run typecheck
- ruff check src/ tests/
- cd frontend && npm run lint
- docker compose build
```

Tất cả CI commands là mandatory. Backend coverage có threshold 85%. Frontend coverage baseline là 11.12% và chưa đặt threshold; frontend test pass vẫn là bắt buộc.

## Analytics regression focus

- Tất cả window `1h`, `4h`, `12h`, `24h`, `7d`, `30d` dùng chung period builder.
- `previous.to == current.from`; hai kỳ liền nhau và không overlap.
- Stage/source/LLM failure vẫn tạo telemetry; thiếu token usage được chấp nhận là 0.
- Cleanup chỉ tác động ba bảng telemetry và giữ event mới hơn 30 ngày.
- Frontend KPI hiển thị previous-period comparison và mở drill-down bằng chuột hoặc bàn phím.
- `/api/stats` vẫn có trong OpenAPI để giữ client cũ tương thích.

## Status (2026-09-13)

- Full backend batch sau hardening: 251 passed, 6 skipped; 87% coverage.
- Frontend: 4 test files / 11 tests passed; typecheck và lint passed.
- `mypy src/` và `ruff check src/` passed.
- Automated tests không gọi external API thật; operational validation được theo dõi riêng trong `EXECUTION/TASKS/TODO.md`.

## Notes

- No real API calls trong automated tests
- Fixtures committed để reproduce
- `test_dagster_lifecycle_parity.py` compares lifecycle identity/count/status, not nondeterministic LLM text

## Dagster shadow verification

The shadow path uses a per-run SQLite namespace and never sends Telegram or
writes `data/scrawlnews.db`. Run the focused checks with:

```bash
pytest -q tests/unit/test_dagster_shadow.py tests/unit/test_dagster_fixtures.py tests/unit/test_dagster_lifecycle_parity.py
```

The archived operational result is in
[2026-09-15-dagster-shadow-comparison.md](../EXECUTION/COMPLETED/reports/2026-09-15-dagster-shadow-comparison.md).

## References

- [setup.md](setup.md) — cài đặt test deps (`make install`, `make test`)
- [PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/02-core-engine.md](../PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/02-core-engine.md) — logic được test
