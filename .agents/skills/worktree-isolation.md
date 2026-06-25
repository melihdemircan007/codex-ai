# Skill: Worktree Isolation

Give each job its **own working directory + branch per affected repo**, so a workflow run never collides
with the main working tree or with another run. Used when the profile sets `isolation: worktree`.
Tool-agnostic — plain `git` so Codex, Cursor, and Claude all follow it.

**Why worktrees, not just branches:** a branch still shares the one working directory. A worktree is a
separate checkout on its own branch — concurrent jobs and your manual work stay independent.

**Repo shape here:** each module is its **own nested git repo** (e.g. `ecom-admin-client` has its own
`.git`, base `origin/releasable` + `origin/integration`). So worktrees are created **per module**.

## Setup (per affected module M, before implementing)

`ROOT` = the monorepo root.

**For `delivery: dual-branch` (this org's model), create BOTH worktrees per repo up front** — one off
`releasable`, one off `integration`:

**First: run the git remote auth preflight** (`.agents/adapters/bitbucket.md`) — it verifies the user's
ambient git credentials (SSH key or credential helper); no token is injected. If it fails, **HALT and
WAIT** and run the adapter's interactive credential flow (collect a username/password → prime the
in-memory cache → re-run the preflight) **before** the `fetch` below — never fetch blindly, and never
proceed past a failed auth check.

```bash
git -C "$ROOT/M" ls-remote origin -h >/dev/null 2>&1 \
    || { echo "git auth missing — see .agents/adapters/bitbucket.md preflight"; exit 1; }
git -C "$ROOT/M" fetch

# releasable worktree — CODE IS AUTHORED HERE
git -C "$ROOT/M" rev-parse --verify "origin/releasable"
git -C "$ROOT/M" worktree add "$ROOT/.worktrees/<JIRA_KEY>/M-releasable" \
    -b "feature/<BRANCH_NAME>-releasable" "origin/releasable"

# integration worktree — RECEIVES the releasable changes at handoff
git -C "$ROOT/M" rev-parse --verify "origin/integration"
git -C "$ROOT/M" worktree add "$ROOT/.worktrees/<JIRA_KEY>/M-integration" \
    -b "feature/<BRANCH_NAME>-integration" "origin/integration"
```

- For `delivery: single-branch`, create just the one worktree off the relevant base.
- If a branch already exists and is the intended work, reuse it (`worktree add <path> <branch>` without
  `-b`); otherwise stop and ask.
- Derive `BRANCH_NAME` from the issue key + sanitized summary (see `.agents/adapters/jira.md`).
- Full-stack jobs → repeat the pair per affected repo (compose with `.agents/skills/multi-repo-feature.md`
  ordering: libraries before consumers; one dev log; one coordinated delivery).
- **Concurrency:** each job gets its **own worktree pair** under `.worktrees/<JIRA_KEY>/` — multiple jobs
  on the same repo run side by side and never touch each other's tree.

## Working in the worktree

- **Code is authored in the `…-releasable` worktree.** All edits, builds, and tests happen inside its
  path, not the main checkout. The `…-integration` worktree stays untouched until handoff.
- `load-context` still works — the worktree contains M's files including its `AGENTS.md` / `docs/`.
- The dual-branch delivery (merge releasable→integration, PR order) is in `.agents/adapters/bitbucket.md`
  and driven by the `handoff` stage.

## Cleanup policy — KEEP (do not auto-remove)

Worktrees are **kept after PR/merge** so you can return to fix a bug from exactly where the work was
done. **Never auto-remove them.**

```bash
git -C "$ROOT/M" worktree list                 # find existing worktrees
git -C "$ROOT/M" worktree remove <path>        # ONLY when the user explicitly asks
git -C "$ROOT/M" worktree prune                # tidy stale entries (manual)
```

## Hygiene

- The worktrees live under `$ROOT/.worktrees/` — ensure `.worktrees/` is in the root `.gitignore`
  (so the root repo doesn't track them).
- Don't nest a worktree inside the module's own tracked tree; keep them under `$ROOT/.worktrees/`.
- **Build caches are shared, not duplicated:** worktrees all use the global `~/.m2` (Maven) and
  `~/.gradle` (Gradle). Builds in a worktree resolve from and cache into the one shared local repo — no
  per-worktree `.m2`, no re-download. Never override `maven.repo.local`.
