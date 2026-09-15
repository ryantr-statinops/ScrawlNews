# Dagster Shadow Comparison — 2026-09-15

## Scope

This comparison validates the Celery/Dagster shadow lifecycle with deterministic
fixtures. It uses a temporary SQLite path, one category, `fetch_limit=2`, and
Telegram disabled. No Internet request, live LLM request, or Telegram delivery is
part of the automated comparison.

The comparison report contains only article identities, counts, statuses, and
runtime metadata. It does not contain article content, summaries, digest payloads,
API keys, bot tokens, or chat IDs.

## Input and isolation

| Setting | Value |
|---|---|
| Category | `technology` |
| Fetch limit | `2` |
| Telegram | disabled; expected sends `0` |
| Database | temporary per-run SQLite fixture |
| Shadow output | isolated namespace; production DB mutation expected `false` |
| LLM | deterministic fallback fixture |

## Results

| Lifecycle measure | Celery fixture | Dagster shadow fixture | Result |
|---|---:|---:|---|
| Article identities | 2 | 2 | Pass |
| Article URLs | 2 | 2 | Pass |
| Duplicate count | 0 | 0 | Pass |
| Summary count | 2 | 2 | Pass |
| Digest count | 1 | 1 | Pass |
| Category mapping | `technology` | `technology` | Pass |
| Fallback summaries | 2 | 2 | Pass |
| Telegram sent | 0 | 0 | Pass |
| Domain DB mutated | false | false | Pass |
| Error stage | none | none | Pass |
| Stage outcomes | equivalent | equivalent | Pass |

## Failure and retry checks

- A deterministic digest-stage partial failure is represented identically by both
  adapters and keeps Telegram delivery at `0`.
- Re-running the same shadow fixture does not add a delivery or duplicate count.
- Production SQLite content hash is unchanged before and after the comparison.
- The serialized comparison report contains no secret field names or values.

## Verification evidence

```text
pytest -q tests/unit/test_dagster_shadow.py tests/unit/test_dagster_fixtures.py
8 passed

pytest -q tests/unit/test_dagster_lifecycle_parity.py
3 passed

ruff check src/dagster_project/comparison.py tests/unit/test_dagster_comparison.py
All checks passed

curl -fsS http://localhost:6767/
pass

curl -fsS http://localhost:6768/server_info
pass

dagster asset list -m src.dagster_project.definitions -d /app
6 assets discovered
```

## Known limitations

This is a deterministic lifecycle comparison, not a live equivalence claim for
RSS parsing or provider-specific LLM output. The live LLM path remains optional
and must use an isolated database and fallback when credentials are unavailable.
Telegram has not been contacted; any future delivery check must use a dedicated
test chat and must not write credentials to logs or reports.

## Conclusion

**PASS for shadow lifecycle safety and fixture parity.** Celery remains the
production orchestrator and scheduler. Dagster remains shadow-only until a live,
isolated comparison and a separate cutover decision are completed.
