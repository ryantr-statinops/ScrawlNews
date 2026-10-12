# ScrawlNews documentation

This documentation describes the checked-in project as it operates today. Execution plans, task backlogs, and release roadmaps are maintained separately under the repository-level `planning/` directory; they are not project reference documentation.

## Start here

- [Product overview](product/overview.md) — purpose, workflows, capabilities, and current limits.
- [System architecture](architecture/system.md) — runtime topology, services, ports, and ownership boundaries.
- [Backend and pipeline](architecture/backend-pipeline.md) — ingestion, Celery lifecycle, retries, delivery, and Dagster shadow assets.
- [Frontend](architecture/frontend.md) — Client routes, Ops mode, analytics, and build modes.
- [Data and storage](architecture/data-and-storage.md) — SQLite ownership, migrations, repositories, and telemetry retention.

## Reference

- [API reference](reference/api.md)
- [Configuration reference](reference/configuration.md)
- [Frequently asked questions](reference/faq.md)
- [Glossary](reference/glossary.md)
- [Architecture decisions](decisions/README.md)

## Operations

- [Local development](operations/local-development.md)
- [Testing and CI](operations/testing.md)
- [Deployment and runtime operations](operations/deployment.md)
- [Backup and recovery](operations/backup-and-recovery.md)
- [Contributor context](operations/agent-context.md)

## History

- [Changelog](history/changelog.md)
- [Verification reports](history/verification-reports/README.md)

## Source-of-truth rules

- Runtime behavior: Python/TypeScript source, Compose configuration, and tests.
- API behavior: FastAPI route definitions. `/metrics` is intentionally excluded from the generated OpenAPI schema.
- Current dependency and verification status: lockfiles, CI workflow, and the latest CI run for the exact source tree.
- Historical verification reports describe only the revision and date stated in each report; they are not current runtime guarantees.
- Target-state ideas and execution plans are not descriptions of implemented behavior.
