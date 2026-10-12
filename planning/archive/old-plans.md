# Old Plans (Archived)

> Plan/task cũ không còn active, chỉ để tham khảo. Đã bị supersede bởi mô hình **4 Stages** trong [ACTIVE_PLANS/roadmap.md](../ACTIVE_PLANS/roadmap.md).

## Superseded: Phase 1–3 model

Trước 2026-08-27, dự án chia theo **Phase 1–3**:

| Phase cũ | Ý định | Thay thế bởi |
|----------|--------|--------------|
| Phase 1: Dashboard MVP + Core Pipeline | → Stage 2 (MVP) + Stage 3 (full 6 features) |
| Phase 2: Production Ready (tests/lint/CI) | → nhập vào Stage 3 (quality) + Stage 4 (CI/GA) |
| Phase 3: Deployment (GA cron) | → Stage 4 (Polish + Deploy) |

### Phase 1 (Unreleased draft — đã bỏ)

- [ ] Scaffolding: requirements, docker-compose, nginx, Makefile, .env, src/+web/
- [ ] Config system: Pydantic Settings mở rộng, hot-reload PUT /api/config
- [ ] Models: Article, Summary, PipelineRun
- [ ] Scrawler/Synthesizer/Messenger services
- [ ] Pipeline orchestration: Celery + FastAPI + SSE
- [ ] SQLite repositories, Dashboard MVP (Feed/Runs/Config)
- [ ] Error handling, logging

> Các mục trên đã được hoàn thành thực tế ở Stage 1–4. Xem [COMPLETED/changelog.md](../COMPLETED/changelog.md).

## Superseded: Original Open Questions (2025-08-21)

Đã resolve và đưa vào ADR (xem [PROJECT_KNOWLEDGE/DECISIONS.md](../../PROJECT_KNOWLEDGE/DECISIONS.md)):

1. Output Language → Tiếng Việt (ADR-006)
2. Deduplication → SHA256(url)[:16] (ADR-007)
3. Error Handling → Graceful degradation (ADR-008)
4. Article Limit → FETCH_LIMIT=20
5. Topic Filtering → lấy tất cả Phase 1, filter sau
6. Interactive Mode → hoãn Phase 4+

## Lưu ý

Không dùng các plan này làm căn cứ implement mới. Luôn tham chiếu [ACTIVE_PLANS/roadmap.md](../ACTIVE_PLANS/roadmap.md) và [TASKS/TODO.md](../TASKS/TODO.md).
