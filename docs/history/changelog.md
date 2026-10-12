# Changelog — historical record

This file records dated implementation and verification milestones. It is not a current-state snapshot or task tracker. Use the [documentation index](../README.md) for current system behavior, and consult each dated [verification report](verification-reports/README.md) for the revision exercised at that time.

## Developer log

### 2025-08-21 — Project planning baseline
- Initial architecture, source, storage, and language decisions recorded in the decision log.

### 2025-08-24 — Hosting and database decisions
- Recorded an initial local SQLite and hosting direction. Later scheduler and local-runtime decisions supersede parts of this baseline; see [architecture decisions](../decisions/decisions.md).

### 2026-08-27 — Dashboard-first pivot
- Recorded the dashboard-first direction and Celery/Redis orchestration decisions.

### 2026-08-27 — Local configuration and parity baseline
- Recorded an early four-setting hot-reload design and an initial local development layout. These are historical choices; see the current [configuration reference](../reference/configuration.md) and [local development guide](../operations/local-development.md).

### 2026-08-28 — Stage 3 and Stage 4 milestones
- Recorded early feature and CI milestones. The test tree and current CI gates have since changed; see [Testing and CI](../operations/testing.md).

### 2026-09-13 — Local Release 1.0 implementation baseline
- Recorded Telegram delivery, frontend cutover, analytics, Agent, backup/restore, CI hardening, and local operational validation at that revision.
- Telegram live delivery with external test credentials remained deferred.

### 2026-09-14 — Release status and lockfile follow-up
- Recorded frontend lockfile metadata updates and Release 1.0's completion-with-exception status.

### 2026-10-02 — Release 1.1 cost guardrails
- Added provider/model price snapshots and a warning-only monthly budget estimate based on token telemetry.
- Recorded backend/API/UI tests for pricing, budget thresholds, missing prices, and persistence errors. Live Telegram delivery remained disabled in the integration run.

### 2026-10-12 — Frontend toolchain audit remediation
- Upgraded `vitest` and `@vitest/coverage-v8` from 3.2.6 to 4.1.11; updated the lockfile, including `source-map-js` 1.2.2.
- On Node 20.19.0 / npm 10.8.2, `npm ci`, audit, lint, typecheck, 106 tests across 22 files, coverage, and Client/Ops builds passed. The audit reported zero vulnerabilities.
- Coverage at that revision: 94.47% lines, 90.63% statements, 85.11% functions, and 87.43% branches. The build still emitted the existing JavaScript chunk-size warning.
