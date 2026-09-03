# SKILL — Folder Structure Đề xuất (Đơn giản, agent nào cũng gọi/tag được)

> Mục tiêu: **đơn giản nhất, flat, không lồng category**, mọi agent (Hermes, Claude, OpenCode, custom) đều discover bằng 1 scan, tag bằng `metadata.tags`.

## Option được chọn: FLAT (khuyến nghị)

```
SKILL/
├── README.md                    # research Hermes vs Claude
├── STRUCTURE.md                 # file này — đề xuất structure
├── scrawler-rss/                # name == directory
│   ├── SKILL.md
│   ├── scripts/
│   │   └── fetch_rss.py
│   └── references/
│       └── RSS_PARAMS.md
├── scrawler-extract/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── extract.py
│   └── references/
├── synthesizer-summarize/
│   ├── SKILL.md
│   └── references/
│       └── PROMPTS.md
├── synthesizer-router/
│   └── SKILL.md
├── messenger-telegram/
│   ├── SKILL.md
│   └── references/
├── dashboard-api/
│   ├── SKILL.md
│   └── references/
├── dashboard-web/
│   ├── SKILL.md
│   └── references/
├── pipeline-control/
│   └── SKILL.md
├── infra-nginx/
│   └── SKILL.md
├── infra-celery/
│   └── SKILL.md
├── infra-go-newsctl/
│   └── SKILL.md
└── _template/
    ├── SKILL.md
    └── references/
```

### Tại sao flat đơn giản hơn nested `category/skill/` cũ?

| Tiêu chí | Nested `SKILL/crawler/rss-fetcher/` (cũ) | Flat `SKILL/scrawler-rss/` (mới) |
|----------|------------------------------------------|----------------------------------|
| **Discovery** | Hermes cần `category/skill` 2 cấp, Claude flat 1 cấp → không tương thích | **Cả 2 đều scan 1 cấp**: `SKILL/*/SKILL.md` — universal |
| **Tag/Gọi** | Phải nhớ category `/crawler/rss-fetcher` | Gọi trực tiếp `/scrawler-rss` hoặc tag search `scrawler` |
| **Tạo mới** | Phải tạo category trước | `mkdir SKILL/my-skill` là xong |
| **Prefix** | Category tách thư mục | Category thành **prefix** `scrawler-*`, `dashboard-*` + `metadata.tags` |

> Flat vẫn giữ được grouping bằng **prefix + tags**, không cần thư mục lồng.

### Quy ước đặt tên & tagging (để agent nào cũng tag được)

Mỗi `SKILL.md`:

```markdown
---
name: scrawler-rss              # == directory name, 1-64 chars, a-z0-9-, không --
description: Fetch Google News RSS and handle feedparser failures. Use when fetching RSS, debugging feed errors, or testing crawler.  # WHAT + WHEN, 1-1024 chars
metadata:
  tags: [scrawler, rss, python, crawler, feedparser]  # để agent tag/search
  category: scrawler           # grouping logic, không phụ thuộc thư mục
  version: "1.0"
---

# Scrawler RSS

## When to Use
- Fetching Google News RSS
- Debugging feedparser

## Procedure
1. ...
```

**Tags gợi ý cho ScrawlNews:**

*   `scrawler`, `synthesizer`, `messenger`, `dashboard`, `infra`, `pipeline` — theo 3 skills + dashboard trong `docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/02-core-engine.md`
*   `python`, `go`, `nginx`, `react`, `celery`, `redis` — theo stack
*   Agent search: `skills_list()` filter `tags contains scrawler` hoặc `description contains rss`

### Tương thích Hermes & Claude với flat

*   **Claude Code**: `~/.claude/skills/` flat — copy/symlink `SKILL/scrawler-rss` → `~/.claude/skills/scrawler-rss` là chạy ngay. Project-level: `ln -s ../../SKILL .agents/skills` hoặc `ln -s ../SKILL .claude/skills`.
*   **Hermes**: `~/.hermes/config.yaml` → `skills.external_dirs: ["./SKILL"]` — Hermes scan external dirs **flat 1 cấp** (mỗi subfolder có `SKILL.md` là 1 skill). Nếu Hermes instance cũ yêu cầu 2 cấp, tạo symlink `SKILL/_flat/scrawler-rss` → vẫn work.
*   **Generic agentskills.io**: `skill-name/SKILL.md` flat là chuẩn spec, `npx skills-ref validate ./SKILL/scrawler-rss` pass.

### Validation

```bash
# validate 1 skill
npx skills-ref validate ./SKILL/scrawler-rss

# validate all
for d in SKILL/*/; do npx skills-ref validate "$d"; done
# hoặc
find SKILL -name SKILL.md -exec dirname {} \; | xargs -I{} npx skills-ref validate {}
```

### Migration từ đề xuất cũ

Nếu đã tạo `SKILL/crawler/rss-fetcher/` → move flat:

```bash
mv SKILL/crawler/rss-fetcher SKILL/scrawler-rss
mv SKILL/synthesizer/summarizer SKILL/synthesizer-summarize
# ... rmdir SKILL/crawler SKILL/synthesizer
```

Giữ `_template/` flat để `cp -r SKILL/_template SKILL/my-new-skill`.

---
*Đề xuất 2026-08-27 — flat prefix + tags, universal cho mọi agent.*
