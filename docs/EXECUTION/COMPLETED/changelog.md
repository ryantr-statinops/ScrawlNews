# Completed — Changelog & Developer Log

> Ghi chép những gì đã hoàn thành. Xem [ACTIVE_PLANS/roadmap.md](../ACTIVE_PLANS/roadmap.md) để biết theo stage.

## Status (2026-08-28)

Stage 1–4 DONE. 77 unit + 10 integration passed, ruff passed, web lint flat. `docker-compose config` + `go run ./cmd/newsctl --help` ok.

## Developer Log

### 2025-08-21 — Project Planning Complete
- Created comprehensive project plan (khi đó ở `docs/plan/`)
- Architecture defined (Service-based, 3 services)
- 8 ADRs recorded — xem [PROJECT_KNOWLEDGE/DECISIONS.md](../../PROJECT_KNOWLEDGE/DECISIONS.md)
- Roadmap 3 phases + milestones, testing strategy, setup/usage guides

### 2025-08-24 — Hosting & Database Decisions
- ADR-010: OmniRoute host Fly.io free tier; DB SQLite local Phase 1, Turso Phase 2+
- Total cost $0/tháng

### 2026-08-27 — Dashboard-First Pivot (ADR-011/012)
- Added ADR-011 (Dashboard-first) + ADR-012 (Celery+Redis)
- Updated PLAN/IMPLEMENT/INDEX, `spec/api.yaml` v0.2.0 (10+ endpoints)
- Choices: Celery+Redis, Nginx, React Vite, docker compose + make dev, keep GA cron, 6 features

### 2026-08-27 — Stage Redefine + Hot-reload + Pure Local + Parity
- Hot-reload chỉ 4 vars đơn giản; secrets/connection phải restart
- DB thuần local `sqlite:///data/scrawlnews.db` cho cả 4 stages
- `make dev` parity Nginx trong Docker + go.mod stub
- Stage 1–3 DONE (`014cc6d`..`b9d0e2c`)

### 2026-08-28 — Stage 3 DONE
- 43 commits Stage 3; fixed 15 tests; verified 77 unit + 10 integration, ruff passed

### 2026-08-28 — Stage 4 DONE
- `.github/workflows/scrawlnews.yml` + `ci.yml`
- `src/main.py` legacy CLI, SETUP.md, Makefile/.gitignore fixes
- Verified `docker-compose config`, `go run ./cmd/newsctl --help`

## Template for Future Entries

```markdown
### YYYY-MM-DD — <Short Title>
**Author**: <Name>
**Completed**:
- Task 1
**Decisions Made**:
- Decision 1 (link ADR nếu mới)
**Next Steps**:
- [ ] Next task 1
```

## Technical Debt Tracker

| Item | Description | Priority | Status |
|------|-------------|----------|--------|
| Config validation | Stricter env var validation | Medium | Pending |
| Circuit breaker | Implement cho LLM API | High | Pending |
| Metrics | Prometheus metrics | Low | Pending |
| Dependency scanning | `pip-audit` trong CI | Medium | Pending |

## Useful Commands

```bash
pytest tests/unit/test_scrawler.py -v
pytest tests/ --cov=src --cov-report=html
mypy src/
ruff check src/ && ruff format src/
LOG_LEVEL=DEBUG python src/main.py --dry-run
rm data/scrawlnews.db && python src/main.py --dry-run
```

## References

- [ACTIVE_PLANS/roadmap.md](../ACTIVE_PLANS/roadmap.md) — stage breakdown
- [TASKS/TODO.md](../TASKS/TODO.md) — remaining work
