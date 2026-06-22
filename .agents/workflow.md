# Agentic Development Workflow (Orchestrator)

> **This is the master loop. Any AI agent (Codex, Claude, Cursor, …) starts here.**
> It is tool-agnostic: it references only files under `.agents/`, never tool-specific config.

## What this is

A **modular, job-driven** workflow. You **take in the job first**, classify it, then a **profile** is
selected. The profile is a small YAML-fronted file that declares *which* stages run, whether tests are
written, how many review passes happen, and which integration adapters are active. You execute the
stages in order, **stopping for explicit user approval at every gate**.

You never run autonomously across a gate. After each stage you post a short report and wait.

## Core loop

```
1. TRIAGE        → read the incoming job lightly; classify it. Recommend a profile + areas with
                   rationale. ALWAYS STOP and wait for the user's approval of the recommendation.
2. SELECT + LOAD → apply the approved profile; read its YAML frontmatter (the "knobs").
3. RUN STAGES    → for each stage in `stages:`, read .agents/stages/<stage>.md and execute it honoring
                   areas / tests / review_passes / reviewers / design_input / clarify_depth / adapters.
4. GATE + REPORT → at every gate in `approval_gates:`, STOP, summarize, wait for explicit "go".
```

## Step 1 — Triage (take in the job first)

**Selecting a profile is NOT the first move — understanding the job is.** Run `.agents/stages/triage.md`:
read the request (and skim the issue summary if a tracker is reachable), then classify:

- **Area(s)** the job touches → `backend`, `frontend`, or **both**.
- Whether a **design** artifact (Figma/screenshots) was provided.
- Whether an **issue key** is present.

From that, recommend a profile + `areas`:

| Job looks like… | Profile | areas |
|---|---|---|
| Backend service/API change (Java/Spring) | `backend-feature` | `[backend]` |
| Frontend/UI change (Angular) | `frontend-feature` | `[frontend]` |
| Touches **both** backend and frontend (e.g. admin API + Angular UI) | `fullstack-feature` | `[backend, frontend]` |
| Dependency / library version bump, no behavior change | `library-bump` | `[backend]` |
| Urgent production fix, minimal ceremony | `hotfix` | per incident |

**Then STOP** (`after_triage`) and present the recommendation with its rationale — e.g. *"This touches
the admin API + Angular UI → `fullstack-feature`, areas=[backend, frontend]. Approve?"* This stop is
**always on**, regardless of the profile's own `approval_gates`. Do not start the full `intake` until
the user approves.

Rules:
- A repo may override defaults with a local `.agents/profile.md` or a nested `AGENTS.md`; if present, it wins.
- The profile is chosen by **the work**, not by the repo. The same repo runs different profiles for different jobs.

## Step 2 — Select the profile + load the knobs

Read the selected profile's frontmatter. The keys you must honor:

| Key | Meaning |
|---|---|
| `areas` | Which parts of the system the job touches: `[backend]`, `[frontend]`, or `[backend, frontend]`. Drives which analyst role(s) and rules apply, how `plan` slices the work, and which test kinds map where. |
| `stages` | Ordered list of stage modules to run (`.agents/stages/<name>.md`). |
| `design_input` | `none` \| `auto` \| `figma` \| `screenshots`. Controls whether `design-analysis` runs. `none` = never; `auto` = only if a design was actually provided (detected at intake); `figma`/`screenshots` = always, from that source. |
| `tests` | List of test kinds to write (`unit`, `api`, `component`, `integration`). **Empty `[]` = write no tests for this job.** |
| `review_passes` | Integer ≥ 1. How many review rounds `review` stage runs. |
| `reviewers` | Lenses each review pass applies (`self`, `security`, `architecture`, …). |
| `clarify_depth` | How hard `clarify` grills: `deep` (full design-tree grill), `light` (only blocking ambiguities), `none` (no grill — `clarify` omitted from `stages`). Default `deep`. |
| `dev_review` | `true`/`false`. When `true`, the `tech-review` stage (between clarify and plan) presents the technical approach and solicits a **developer comment** that can reshape the approach or send it back to re-analyze. Default `false`. |
| `isolation` | `worktree`/`in-place`. `worktree` = each affected repo gets its own **git worktree** (own working dir + branch) so jobs/runs never collide; worktrees are **kept** (manual cleanup). `in-place` = branch in the main working tree. See `.agents/skills/worktree-isolation.md`. |
| `delivery` | `dual-branch`/`single-branch`. `dual-branch` = author in the `…-releasable` worktree, merge into the `…-integration` worktree (resolve conflicts), then open the **integration PR first**, then the **releasable PR** — each its own approval, all logged to the Jira dev log. `single-branch` = one branch, one PR. See `.agents/adapters/bitbucket.md`. |
| `adapters` | Integrations to activate (`jira`, `bitbucket`, `jenkins`). Empty = none; intake falls back to the prompt. |
| `approval_gates` | Where to STOP for explicit user approval (e.g. `after_clarify`, `after_plan`, `before_pr`). The `after_triage` stop is always on, on top of these. |

If a key is absent in the profile, use these defaults: `areas: [backend]`, `tests: [unit]`,
`review_passes: 1`, `reviewers: [self]`, `clarify_depth: deep`, `adapters: []`,
`approval_gates: [after_plan]`.

## Step 3 — Run the stages

For each entry in `stages:`, open `.agents/stages/<stage>.md` and follow it. Stages are
parametrized by the knobs:

- **`load-context` loads repo-local guidance first.** Right after `intake`, for each target module it
  discovers and reads that repo's own rules/skills/docs (`.cursor/rules`, `.cursor/skills`, `AGENTS.md`,
  `CLAUDE.md`, `docs/*`) via `.agents/skills/local-rules-discovery.md`. **Local guidance overrides the
  root `.agents/` defaults on conflict (closest-wins).** Never edit a repo whose guidance wasn't loaded.
- **`areas` selects the analyst role(s) and rules.** For each area: `backend` → `backend-analyst` +
  `.agents/rules/java-backend.md`; `frontend` → `frontend-analyst` + `.agents/rules/angular-frontend.md`.
  When `areas` has both, `intake`/`clarify`/`plan` cover both, and `plan` produces per-area execution
  slices with the **backend contract slice implemented before the frontend slice** (see
  `.agents/skills/multi-repo-feature.md`): one branch per repo, one dev log, one coordinated PR cycle.
- `design-analysis` runs when `design_input` is `figma`/`screenshots`, **or** when `design_input: auto`
  **and** a design artifact was provided (per `intake`). It applies only to the `frontend` area.
  Otherwise it self-skips — design is optional.
- `clarify` grills at `clarify_depth`: `deep` = walk the design tree branch by branch; `light` = only
  blocking decisions; `none` = omitted from `stages`. **Every decision it surfaces — open *or*
  evidence-backed — needs the user's explicit approval; nothing auto-closes.** It cannot exit (or jump
  to implement) until the whole decision ledger is user-approved.
- `tech-review` runs between `clarify` and `plan` **only when `dev_review: true`**; it posts the
  technical approach and asks for a developer comment, then adjusts / loops back to clarify-intake /
  proceeds. Self-skips when `dev_review: false`. Comment-driven changes go into the Decision Checklist.
- **`isolation` controls where code is written.** When `worktree`, set up and work inside the job's
  **git worktree** per `.agents/skills/worktree-isolation.md`; the main working tree stays untouched and
  worktrees are **kept** for later bugfix continuation. When `in-place`, branch in the main tree as usual.
- **`delivery` controls how the change ships.** When `dual-branch`, the job uses a worktree **pair** per
  repo (`…-releasable` + `…-integration`): code is authored on releasable, merged into integration
  (conflicts resolved), then `handoff` opens the **integration PR first, then the releasable PR** — each
  a separate approval, every step logged to the Jira dev log (`.agents/adapters/bitbucket.md`).
- `test` writes **only** the kinds listed in `tests`; if `tests: []` it is a no-op (state this explicitly in the report).
- `review` runs `review_passes` rounds, each applying the `reviewers` lenses.
- Adapter-backed stages (`intake` via Jira, `handoff` via Bitbucket/Jenkins) only call an
  integration that is listed in `adapters`. If not listed, use the local fallback the adapter file documents.

Stages reference **roles** (`.agents/roles/*.md`) for the persona to adopt, and **skills**
(`.agents/skills/*.md`) / **rules** (`.agents/rules/*.md`) for repo conventions.

## Step 4 — Gate and report

At every gate named in `approval_gates`, post a compact report and **STOP**:

```
### <Stage> complete — awaiting approval
- What I did: …
- Key decisions / findings: …
- Knobs in effect: areas=…, tests=…, review_passes=…, clarify_depth=…, adapters=…
- Next stage: <name> — proceed?
```

Do not cross the gate until the user explicitly approves. Approval for one gate is **not**
approval for later gates (e.g. "implement" ≠ "open a PR"). Destructive or outward-facing actions
(push, open PR, rerun CI, merge, hand off to QA) always require their own approval.

## Non-negotiable rules

- **Approval-first.** Never auto-proceed across a gate — and never start work before the user approves
  the triage recommendation (`after_triage`).
- **Take in the job before choosing a profile.** Triage first; classify area(s); recommend, then wait.
- **Load a repo's own guidance before editing it.** `load-context` runs after intake; nested/local
  rules take precedence over root defaults (closest-wins). Never write code in a repo blind.
- **Auth preflight before any remote op.** Before reading Jira, run the Jira credential preflight
  (`JIRA_BASE_URL` / `JIRA_PERSONAL_TOKEN` — `.agents/adapters/jira.md`). Before any network git op
  (`fetch`/`worktree add origin/<base>`/push/PR), run the **git remote auth preflight** —
  `git ls-remote` against the user's ambient credentials (`.agents/adapters/bitbucket.md`). If either
  fails, **stop and ask the user to set up auth** (Jira token / git SSH or credential helper) — don't
  blindly `fetch` or call the integration.
- **On git auth failure: HALT and WAIT.** Do not run any further stage. Offer the user the choice to fix
  ambient auth or **enter a git username/password now**; cache it in memory only (`.agents/adapters/bitbucket.md`)
  and resume **only after the preflight passes**. Never proceed past a failed auth check.
- **Requirement traceability.** Keep one Decision Checklist from `clarify`; mark overridden decisions
  `superseded` (never silently drop); keep a separate **Must-Not-Exist** list for negative requirements;
  verify every item against code in `review`; **don't mark the job done if a single item is unmet or
  contradicted.** See `.agents/rules/requirement-traceability.md`.
- **Smallest safe change** that satisfies the acceptance criteria; no unrelated refactors.
- **Secrets stay out of the repo and chat.** Use environment variables / runtime config only;
  never print tokens. (See `.agents/adapters/*.md`.)
- **Job-driven, not repo-driven.** Pick the profile from the work.
- **Modularity.** Each stage/role/adapter/rule/skill is one self-contained file. To change
  behavior, edit one module — don't rewrite the orchestrator.

## Extending the system

See `.agents/README.md` for how to add a profile, edit a stage, or write a new adapter.
