# 05 — Extensibility

> Khả năng mở rộng: Security, Skill System. Gom cả bảo mật.

## Principles

- Flat skill với `metadata.tags`, không lồng category
- Security: secrets qua env vars, không hardcode

---

## Security

> Bảo mật, phân quyền, mã hóa.

### Current

- Secrets chỉ qua env vars, không log
- `telegram_enabled` toggle
- SQLite file permissions 600 trên runner

### Future

- Plugin hooks, SDK extensibility

### Implementation

- `src/config.py` validator `telegram_enabled` yêu cầu `TELEGRAM_BOT_TOKEN`
- `.gitignore` secrets (`3dcc91f`)
- `.github/workflows` dùng GitHub Secrets

## Skill System

> Flat tagging cho mọi agent.

### Structure

```
.agent/SKILL/<skill>/SKILL.md  # name == dir, tags: [scrawler, rss]
```

### Discovery

- agentskills.io 3 levels: metadata, instructions, resources
- Hermes `external_dirs`, Claude `.agents/skills` đều scan flat

### Implementation (Stage 1–2)

- Stage 1: `.agent/SKILL/_template` flat, STRUCTURE flat proposal — `2f93c41`, `_template` — `a741eed`
- Stage 2: commit-workflow skill — `b9ba36f`, move SKILL → `.agent/SKILL` — `2cc0ec9`
- Stage 3–4: web lint flat — `b9d0e2c`, `.github workflows` — `0f328aa`..`60b8bba`, SETUP.md — `e4d43b8`

## References

- `.agent/SKILL/README.md`, `.agent/SKILL/STRUCTURE.md`
- `.agent/SKILL/commit-workflow/SKILL.md`
- [DECISIONS.md](../DECISIONS.md) — ADR-009 (security context)
