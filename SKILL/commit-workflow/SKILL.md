---
name: commit-workflow
description: Enforce atomic commits with immediate push. Use when working on any task, editing files, or completing work that requires git history. Triggers on task execution, file changes, or before reporting completion.
metadata:
  tags: [git, commit, push, workflow, atomic]
  category: infra
  version: "1.0"
---

# Commit Workflow

## When to Use
- Working on any task that modifies files
- Completing a subtask or logical unit of work
- Before reporting task completion to user
- When AGENTS.md commit rule applies

## Procedure
1. Split work into smallest logical units. One commit per file or per coherent change, never combine unrelated changes.
2. Before committing, check current branch with `git branch --show-current` and `git status -sb`.
3. Stage only intended files with `git add <path>`. Verify with `git diff --cached --stat`.
4. Commit with conventional message `type(scope): description` using `git commit -m "type(scope): message"`.
5. Push immediately after commit. If on main or master, push directly to origin. If on feature branch, push to the branch for PR.
6. Report commit hash and summary after each push before proceeding to next unit.
7. Never create empty commits, never skip hooks, never force push unless explicitly requested.
8. If commit fails due to hooks, fix the issue and create a new commit, do not amend the failed one.

## Pitfalls
- Combining multiple unrelated changes into one commit breaks atomicity and reviewability
- Forgetting to push after commit leaves remote out of sync
- Staging unintended files including secrets or .env
- Amending a failed commit instead of creating a new one

## Verification
- Run `git log --oneline -3` to confirm commit exists locally
- Run `git status -sb` to confirm branch is up to date with origin
- Confirm remote received commit via `git push` output
- Each commit should be small, focused, and push succeeds without errors

## References
- See `.agent/AGENTS.md` for project commit rule
- See `SKILL/_template/SKILL.md` for skill format
