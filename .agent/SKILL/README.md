# SKILL Organization — Research & Proposal for ScrawlNews

> Tổng hợp cơ chế SKILL từ **Hermes Agent** (Nous Research) và **Claude** (Anthropic) + **agentskills.io** open standard, và đề xuất cấu trúc cho `SKILL/` trong ScrawlNews.

## 1. agentskills.io — Open Standard (cơ sở chung)

Cả Hermes và Claude đều tương thích với [agentskills.io/specification](https://agentskills.io/specification). Đây là spec trung lập:

### Directory structure chuẩn

```
skill-name/
├── SKILL.md          # Required: metadata + instructions (YAML frontmatter + markdown)
├── scripts/          # Optional: executable code (python/bash/js)
├── references/       # Optional: docs chuyên sâu (REFERENCE.md, FORMS.md)
├── assets/           # Optional: templates, images, data
└── ...               # bất kỳ file khác
```

### SKILL.md format

```markdown
---
name: skill-name              # 1-64 chars, lowercase a-z0-9-, match directory, không --, không - đầu/cuối
description: What it does and when to use it. Use when ...  # 1-1024 chars, phải nói cả WHAT + WHEN
license: Apache-2.0           # optional
compatibility: ...            # optional
metadata:
  author: org
  version: "1.0"
allowed-tools: ...            # optional (experimental)
---

# Skill Title
## When to Use
...
## Procedure
...
```

*   **Validation**: `skills-ref validate ./my-skill`
*   **Progressive disclosure 3 levels** (cả Hermes & Claude dùng):
    1.  **Metadata** ~50-100 tokens/skill — chỉ `name` + `description` load lúc startup
    2.  **Instructions** <5k tokens — full `SKILL.md` body load khi trigger
    3.  **Resources** as needed — `scripts/`/`references/` load riêng khi cần (script chỉ output vào context, không load code)

> Quy tắc: `SKILL.md` <500 lines, chi tiết tách ra `references/`.

## 2. Hermes Agent — Cơ chế tổ chức

**Source**: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills

### Vị trí & phân cấp

```
~/.hermes/skills/                  # Single source of truth (primary, read-write)
├── mlops/
│   ├── axolotl/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── templates/
│   │   ├── scripts/
│   │   ├── examples/
│   │   └── assets/
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # agent-created skill
│       └── SKILL.md
├── .hub/                          # Hub state: lock.json, quarantine/, audit.log
└── .bundled_manifest
```

*   **Category directory** (`mlops/`, `devops/`, `research/`… 20+ categories) → mỗi skill là subfolder.
*   **External dirs**: `~/.hermes/config.yaml` → `skills.external_dirs: [~/.agents/skills, /team/skills]` — scan thêm, local precedence nếu trùng tên.
*   **Project-local skills** (cao nhất): `<project>/.hermes/skills/` hoặc `<project>/.agents/skills/` — chỉ active khi `hermes` chạy trong repo đó + `hermes skills trust` + scan quarantine (content-hash cache `~/.hermes/cache/project_skill_scans/`). Precedence: `project > local > external_dirs`.
*   **Bundles**: `~/.hermes/skill-bundles/<slug>.yaml` — group nhiều skill dưới 1 slash command (`hermes bundles create backend-dev --skill a --skill b`).
*   **Slash commands**: `/<skill-name>` → load skill; có thể stack `/a /b do X` (tối đa 5).

### SKILL.md mở rộng Hermes

```yaml
---
name: my-skill
description: Brief description (shown in search)
version: 1.0.0
platforms: [macos, linux]   # restrict OS
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]   # chỉ hiện khi toolsets thiếu
    requires_toolsets: [terminal]  # chỉ hiện khi có
    config:
      - key: myplugin.path
        description: Plugin data dir
        default: "~/myplugin-data"
        prompt: Path prompt
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: https://...
---
```

*   **Secure setup on load**: khai báo `required_environment_variables` → Hermes hỏi secret khi load (không hỏi trên messaging), auto passthrough vào `terminal`/`execute_code`.
*   **Progressive**: `skills_list()` ~3k tokens → `skill_view(name)` full → `skill_view(name, path)` file cụ thể. Dashboard có nút **Learn a skill** (`/learn`).
*   **Agent-managed**: `skill_manage` tool (`create/patch/edit/delete/write_file/remove_file`) + `skills.write_approval` gate → staged `~/.hermes/pending/skills/`.

### Hub & Security

*   `hermes skills browse/search/inspect/install/update/tap` với sources: `official`, `skills-sh`, `well-known`, `github`, `clawhub`…
*   Scan quarantine: `dangerous` verdict → không index, lock.json ghi hash + findings.

## 3. Claude — Cơ chế tổ chức

**Source**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview + https://code.claude.com/docs/en/skills

### Vị trí & discovery

| Scope | Path | Ghi chú |
|-------|------|---------|
| **User cross-client** | `~/.agents/skills/` | Standard `agentskills.io` |
| **User Claude-specific** | `~/.claude/skills/` | `~/.claude/skills/<skill>/SKILL.md` |
| **Project cross-client** | `.agents/skills/` | Highest precedence |
| **Project Claude-specific** | `.claude/skills/` | `.claude/skills/<skill>/SKILL.md` |
| **API** | Upload via `/v1/skills` | workspace-wide, cần `code execution` tool, sandboxed no network |

*   Cũng dùng **progressive disclosure 3 levels** y hệt:
    *   L1 Metadata always (~100 tokens/skill) in system prompt
    *   L2 Instructions khi trigger (`cat SKILL.md`)
    *   L3 Resources as needed ( `FORMS.md`, `scripts/fill_form.py` — scripts chạy qua bash, chỉ output vào context)

### Frontmatter constraints (nghiêm hơn Hermes)

*   `name`: 1-64 chars, `^[a-z0-9-]+$`, không `anthropic`/`claude`, không `--`, không `-` đầu/cuối, phải == directory name
*   `description`: 1-1024 chars, non-empty, không XML tags, phải nói **what + when** (dùng imperative `Use when...`)

### Khác biệt với Hermes

*   **Không có category directory** bắt buộc — flat `~/.claude/skills/<skill>/`. Hermes bắt buộc `category/skill/`.
*   **Không có bundles Hub tích hợp sẵn** như Hermes — Claude dùng `plugins` để bundle nhiều skill.
*   **Không có project trust gate** — `.claude/skills/` auto load nếu trong repo, không cần `trust`.
*   **API constraints**: skills chạy trong container no network, no runtime `pip install` — chỉ pre-installed packages.

## 4. So sánh nhanh

| Tiêu chí | Hermes | Claude | ScrawlNews đề xuất |
|----------|--------|--------|-------------------|
| **Standard** | agentskills.io + mở rộng hermes metadata | agentskills.io thuần | **agentskills.io** (tương thích cả 2) |
| **Location** | `~/.hermes/skills/category/skill/` | `~/.claude/skills/skill/` hoặc `.agents/skills/skill/` | `SKILL/<category>/<skill>/` (uppercase theo yêu cầu) + có thể symlink ra `.agents/skills/` để tương thích |
| **Category** | Bắt buộc | Không bắt buộc | **Có** (để scale, giống 3 skills + dashboard trong `docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/02-core-engine.md`) |
| **Progressive** | 3 levels, `skills_list`/`skill_view` | 3 levels, metadata/instructions/resources | **3 levels** — giữ `SKILL.md` <500 lines |
| **Trust** | `hermes skills trust` + quarantine scan | Auto load project skills | **Không cần trust gate** (local dev thuần túy) |
| **Scripts** | `scripts/` + auto passthrough env | `scripts/` chạy via bash, chỉ output | **Giữ** |
| **Tool** | `skill_manage`, bundles | Không | **Không** — ScrawlNews tự manage |

## 5. Đề xuất cấu trúc `SKILL/` cho ScrawlNews

> Yêu cầu: thư mục tên `SKILL` (uppercase) ở root, trọng tâm Python + Go + Traefik(đã chuyển Nginx) + React. Tương thích agentskills.io để Hermes/Claude đều đọc được.

### Cấu trúc đề xuất

```
SKILL/
├── README.md                     # file này
├── crawler/                      # Category: thu thập (Scrawler)
│   ├── rss-fetcher/
│   │   ├── SKILL.md              # name: rss-fetcher, description: Use when fetching Google News RSS...
│   │   ├── scripts/
│   │   │   └── fetch_rss.py
│   │   └── references/
│   │       └── RSS_PARAMS.md
│   └── content-extractor/
│       ├── SKILL.md
│       ├── scripts/
│       │   └── extract.py        # trafilatura fallback chain
│       └── references/
│           └── EXTRACTION_BENCHMARK.md
├── synthesizer/
│   ├── summarizer/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── summarize.py
│   │   └── references/
│   │       └── PROMPTS.md
│   └── llm-router/
│       ├── SKILL.md              # OpenRouter/OmniRoute routing
│       └── references/
├── messenger/
│   └── telegram-delivery/
│       ├── SKILL.md
│       ├── scripts/
│       │   └── send.py
│       └── references/
│           └── FORMATTING.md
├── dashboard/
│   ├── api/
│   │   ├── SKILL.md              # FastAPI + Celery
│   │   └── references/
│   │       └── ENDPOINTS.md
│   ├── web/
│   │   ├── SKILL.md              # React Vite + TanStack Query
│   │   └── references/
│   └── pipeline-control/
│       ├── SKILL.md
│       └── scripts/
├── infra/
│   ├── nginx-gateway/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── NGINX_CONF.md
│   ├── celery-worker/
│   │   ├── SKILL.md
│   │   └── references/
│   └── go-newsctl/
│       ├── SKILL.md              # go.mod stub Cobra
│       └── scripts/
└── _template/                    # template để tạo skill mới
    ├── SKILL.md
    ├── scripts/
    └── references/
```

### Quy ước đặt tên

*   Mỗi skill: `SKILL/<category>/<skill-name>/SKILL.md` với `name` == directory name (lowercase hyphen, 1-64 chars)
*   `description` phải imperative: `Use when ...` (ví dụ: `Use when fetching Google News RSS or debugging feedparser failures`)
*   `SKILL.md` giữ <500 lines, chi tiết tách `references/`, script tách `scripts/`
*   Category gợi ý: `crawler`, `synthesizer`, `messenger`, `dashboard`, `infra` — ánh xạ 1-1 với 3 skills + dashboard trong `docs/PROJECT_KNOWLEDGE/DOMAIN_CONCEPTS/02-core-engine.md`

### Tương thích

*   **Hermes**: symlink hoặc `skills.external_dirs: [./SKILL]` trong `~/.hermes/config.yaml` → Hermes sẽ scan `SKILL/crawler/rss-fetcher/` như external skill
*   **Claude**: symlink `./SKILL` → `.agents/skills/` hoặc copy — Claude Code sẽ `cat SKILL.md` progressive
*   **Validation**: `npx skills-ref validate ./SKILL/crawler/rss-fetcher`

### Bước tiếp theo (khi bạn cho phép)

1. Tạo 1 skill mẫu `SKILL/crawler/rss-fetcher/SKILL.md` theo template agentskills.io
2. Tạo `_template/SKILL.md` để team tạo skill mới nhanh
3. (Optional) Thêm script `SKILL/scripts/validate-all.sh` chạy `skills-ref validate` cho CI

---
*Research 2026-08-27 — sources: hermes-agent.nousresearch.com/docs/user-guide/features/skills, platform.claude.com/docs/en/agents-and-tools/agent-skills/overview, agentskills.io/specification*
