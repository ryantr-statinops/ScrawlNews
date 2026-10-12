# Testing and CI

## Local commands

From the repository root:

```bash
make test
make lint
make typecheck
```

`make test` runs `pytest tests/ --cov=src --cov-report=term-missing`, then `npm run test` in `frontend/`. It does not pass CI's backend `--cov-fail-under=85` flag and does not run `npm audit`; use the CI commands below when you need to reproduce gates.

Frontend-specific commands:

```bash
cd frontend
npm run test
npm run test:coverage
npm run lint
npm run typecheck
npm run build:client
npm run build:ops
```

## Coverage gates

- Backend CI runs `pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=85`.
- Frontend Vitest uses the V8 provider, includes `src/**/*.{ts,tsx}` with explicit exclusions in `frontend/vite.config.ts`, and requires at least 80% for lines, statements, functions, and branches.

Thresholds are CI contracts; do not weaken them to make a failing run pass.

## Pull-request and main CI

`.github/workflows/ci.yml` runs on pushes and pull requests targeting `main`. It installs Python 3.11 and Node 20.19.0, installs locked frontend dependencies with `npm ci`, runs `npm audit --audit-level=high`, Ruff, ESLint, MyPy, TypeScript typecheck, backend/frontend coverage suites, and `docker compose build`.

The scheduled workflow is separate from CI. It runs `pip-audit` and a non-delivery CLI smoke on a temporary SQLite database; it does not establish successful live Telegram delivery or a hosted deployment.

## Test inventory

The checked-in test tree is the definitive test inventory: backend tests are under `tests/unit/` and `tests/integration/`; frontend tests are under `frontend/src/__tests__/`. Older test-tree diagrams and historical test counts in reports describe their dated revision, not the current suite.
