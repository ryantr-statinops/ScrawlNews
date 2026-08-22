# Implementation Notes

Ghi chép quá trình implement ScrawlNews — Changelog & Developer Notes.

## Changelog

### [Unreleased] — Development Phase

#### Phase 1: Core Pipeline (In Progress)
- [ ] Project scaffolding: `requirements.txt`, `Makefile`, `.env.example`, `src/` structure
- [ ] Config system: Pydantic Settings
- [ ] Models: `Article`, `Summary` dataclasses
- [ ] ScrawlerService: RSS fetch + Trafilatura extract; fallback: Readability-lxml → Playwright
- [ ] SynthesizerService: OpenRouter/9router batch summarization
- [ ] MessengerService: Telegram Bot send with formatting
- [ ] Pipeline orchestration: `main.py` with CLI args
- [ ] SQLite repositories: ArticleRepo, SummaryRepo
- [ ] Error handling: retry, circuit breaker, graceful degradation
- [ ] Logging: structured JSON logging

#### Phase 2: Production Ready (Planned)
- [ ] Unit tests (target >90% coverage)
- [ ] Integration tests
- [ ] Lint (ruff), typecheck (mypy), pre-commit
- [ ] CI workflow: lint + test on PR

#### Phase 3: Deployment (Planned)
- [ ] GitHub Actions workflow with cron
- [ ] Secrets configuration
- [ ] Verify automated runs

---

## Developer Log

### 2025-08-21 — Project Planning Complete
**Author**: AI Assistant

**Completed**:
- Created comprehensive project plan in `docs/plan/`
- Architecture defined (Skill-based Agent, 3 services)
- Technical decisions recorded in `decisions.md` (8 ADRs)
- Future ideas captured in `ideas.md`
- Roadmap with 3 phases + milestones
- Testing strategy defined
- Setup & usage guides written

**Key Decisions**:
1. **Data Source**: Google News RSS + trafilatura (primary), Playwright fallback
2. **LLM**: OpenRouter / 9router (Phase 1: OpenRouter; Phase 2+: 9router auto-fallback)
3. **Storage**: SQLite (file-based, zero-config)
4. **Orchestration**: Single async Python script (`main.py`)
5. **Deployment**: GitHub Actions (free, cron support)
6. **Language**: Vietnamese output, English code/docs
7. **Dedup**: SHA256(URL)[:16] as deterministic ID
8. **Error Handling**: Graceful degradation per component

**Open Questions** (tracked in `technical-deep-dive.md`):
- Exact Google News RSS query params for categories
- trafilatura extraction quality on VN news sites
- Playwright stealth effectiveness
- Token cost optimization strategies

---

### Template for Future Entries

```markdown
### YYYY-MM-DD — <Short Title>
**Author**: <Name>

**Completed**:
- Task 1
- Task 2

**Issues Encountered**:
- Issue 1 → Solution
- Issue 2 → Workaround

**Decisions Made**:
- Decision 1 (link to ADR if new)

**Next Steps**:
- [ ] Next task 1
- [ ] Next task 2
```

---

## Technical Debt Tracker

| Item | Description | Priority | Status |
|------|-------------|----------|--------|
| Config validation | Add stricter env var validation | Medium | Pending |
| Circuit breaker | Implement for LLM API | High | Pending |
| Metrics | Add Prometheus metrics | Low | Pending |
| Dependency scanning | Add pip-audit to CI | Medium | Pending |

---

## Useful Commands During Development

```bash
# Run single test file
pytest tests/unit/test_scrawler.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Type check
mypy src/

# Lint & format
ruff check src/ && ruff format src/

# Debug pipeline
LOG_LEVEL=DEBUG python src/main.py --dry-run

# Reset DB
rm data/scrawlnews.db && python src/main.py --dry-run
```