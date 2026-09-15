# Completed — Changelog & Developer Log

> Ghi chép những gì đã hoàn thành. Xem [ACTIVE_PLANS/roadmap.md](../ACTIVE_PLANS/roadmap.md) để biết theo stage.

## Current verification pointer

Trạng thái hiện tại và kết quả verification mới nhất được duy trì tại [CURRENT_STATE.md](../../PROJECT_KNOWLEDGE/CURRENT_STATE.md). Các mốc bên dưới là nhật ký lịch sử và giữ nguyên số liệu tại thời điểm hoàn thành.

## Developer Log

### 2026-09-15 — Agent Context Gateway
- README có protocol đọc context, kiểm tra Git state và compact handoff checklist.
- Thêm `PROJECT_KNOWLEDGE/AGENT_CONTEXT.md` làm context ổn định cho agent; branch, commit, test và runtime status vẫn phải kiểm tra trực tiếp.
- Thêm validation cho links, required sections, ports, review date và secret-pattern safety.
- Quy ước: thay đổi lớn cập nhật context/current state; thay đổi nhỏ chỉ ghi changelog; session handoff dùng task docs và Git history.

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

### 2026-09-13 — Local Release 1.0 implementation baseline

**Completed**:
- Interactive Telegram bot, category filtering, LLM/Telegram circuit breaker và graceful Telegram configuration.
- Product frontend cutover, Analytics Command Center và telemetry retention 30 ngày.
- Agent v1 deterministic policy, approval gate, SQLite audit trail, database backup và pipeline dry-run queue.
- SQLite backup/restore; `pip-audit` đã có trong scheduled workflow.
- Backend batch suite không còn treo trong verification local: 251 passed, 6 skipped; frontend 11 passed; MyPy, frontend typecheck/lint và Ruff `src/ tests/` passed.
- Execution model đã chốt theo ADR-014: Celery Beat local là production scheduler; GitHub Actions là daily non-delivery smoke. Beat dùng chung SQLite volume với dashboard.
- Operational validation: 3 isolated runs xác nhận RSS/fallback và RSS/OpenRouter paths; sửa package-module CLI invocation, total fetch-limit enforcement và LLM async-client lifecycle. Telegram test delivery còn chờ credentials.
- CI hardening: bỏ toàn bộ soft-fail, bắt buộc lint/typecheck/tests/Docker build, backend coverage threshold 85%, `npm ci` và frontend Docker context tối giản.
- Post-1.0 roadmap đã được sắp theo reliability-first: frontend toolchain security → metrics → config validation → cost guardrails → source reliability/coverage; source expansion và news intelligence theo sau.

**Not yet operationally validated**:
- Chuỗi 2–3 runs theo ba tầng với RSS/LLM/Telegram thật.
- Telegram live delivery với test-chat credentials vẫn deferred; không phải blocker runtime khi tắt Telegram.

### 2026-09-14 — Release status and lockfile follow-up
- Chuẩn hóa metadata lockfile frontend trong commit độc lập; không thay đổi version Vite/Vitest.
- Release 1.0 được ghi nhận **Complete with exception** vì Telegram live validation cần external test credentials.

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
| Circuit breaker | Implement cho LLM và Telegram | High | Complete |
| Metrics | Prometheus metrics | Low | Pending |
| Dependency scanning | `pip-audit` trong scheduled workflow | Medium | Complete |
| Operational validation | 2–3 runs với external services thật | High | Pending |
| CI hardening | Bỏ soft-fail theo từng gate đã verify | High | Complete |
| Frontend dependency security | Vite/Vitest audit findings cần major migration | High | Pending |
| Frontend coverage | Baseline 11.12%, chưa có threshold | Medium | Pending |

## Useful Commands

```bash
pytest tests/unit/test_scrawler.py -v
pytest tests/ --cov=src --cov-report=html
mypy src/
ruff check src/ && ruff format src/
LOG_LEVEL=DEBUG python -m src.main --dry-run
rm data/scrawlnews.db && python -m src.main --dry-run
```

## References

- [ACTIVE_PLANS/roadmap.md](../ACTIVE_PLANS/roadmap.md) — stage breakdown
- [TASKS/TODO.md](../TASKS/TODO.md) — remaining work
