# `.agents/` — Modular Agentic Workflow

One tool-agnostic source of truth that drives **Codex, Claude Code, Cursor, or any AI agent**. The
agent enters at the root `AGENTS.md`, which sends it to `.agents/workflow.md` (the orchestrator).

## Why it's built this way

- **Tool-agnostic.** All logic lives in `.agents/`. `AGENTS.md` (Codex/Cursor/others) and `CLAUDE.md`
  (`@AGENTS.md` import) point at the same files — zero drift across tools.
- **Take in the job first.** Step 1 is **triage** — the agent reads the incoming job, classifies its
  area(s) (backend / frontend / both), and **recommends a profile, then stops for your approval**.
  Profile selection follows understanding, not the other way round.
- **Load each repo's own guidance before editing it.** The `load-context` stage (right after intake)
  discovers and reads a target repo's local rules/skills/docs (`.cursor/rules`, `.cursor/skills`,
  `AGENTS.md`, `CLAUDE.md`, `docs/*`). **Nested/local guidance wins over the root defaults** (closest-wins).
- **Job-driven, not repo-driven.** The *work* picks a **profile**; the same repo runs different
  profiles for different jobs (a frontend job uses design analysis, a backend job doesn't).
- **Modular.** Each concern is one file. Change behavior by editing one module — never the orchestrator.
- **Approval-first.** Every profile defines gates where the agent stops and waits for an explicit "go".
  At the **clarify** gate this means **every** decision — open *or* evidence-backed — is surfaced for
  your explicit approval; nothing is silently closed, and the agent can't proceed until you've approved
  the whole decision ledger.
- **Requirement traceability.** One Decision Checklist runs clarify → plan → implement → review →
  handoff; overridden decisions are marked `superseded` (never dropped), negative requirements live in a
  **Must-Not-Exist** list, and the job isn't "done" until every item is verified against the code
  (incl. Must-Not items confirmed absent). See `rules/requirement-traceability.md`.
- **Auth preflights, not blind failures.** Before reading Jira (`adapters/jira.md`) the workflow checks
  `JIRA_BASE_URL`/`JIRA_PERSONAL_TOKEN`; before any `fetch`/worktree/push/PR (`adapters/bitbucket.md`) it
  runs `git ls-remote` against your **ambient git credentials** (SSH key or OS credential helper — no
  token is injected). If git auth fails it **halts and waits** — you can fix ambient auth or **enter a
  git username/password to continue** (cached in memory only, never written to the repo/URL); the run
  resumes only after the preflight passes. Offline / `isolation: in-place` is also offered.
- **PRs are headless Bitbucket REST** (no browser, ever). **No `BITBUCKET_*` env vars** — base/project/slug
  are derived from the git remote and auth reuses **git's own credential** (`git credential fill`, the same
  creds as `git push`). On HTTP 401/403 the workflow halts and sets up the git credential
  (`git credential approve`), then retries — it never prompts for env tokens or a browser.
- **The CI build gate + failure diagnosis use Jenkins directly** (`JENKINS_URL` / `JENKINS_USER` /
  `JENKINS_PASSWORD` + `JENKINS_JOB_PREFIX`, kept in `.env.local`). On a red `lastBuild`, the workflow reads
  Jenkins console/test/stage output, classifies the failure, and **resumes the mapped stage** (test →
  implement→test, Sonar → implement→review, deploy/infra → re-trigger/escalate) — fix loop capped at
  `ci_fix_attempts`. The releasable PR opens only on a green Jenkins build.

## Directory map

```
workflow.md     orchestrator (start here)
profiles/       job profiles = composition + knobs (YAML frontmatter)
stages/         reusable steps: triage, intake, load-context, design-analysis, clarify, tech-review, plan, implement, test, review, handoff
roles/          personas: frontend-analyst, backend-analyst, implementer, tester, reviewer
adapters/       optional integrations: jira, bitbucket, jenkins (+ templates/)
rules/          conventions + policy: java-backend, angular-frontend, testing-standards, requirement-traceability
skills/         how-tos: endpoint-discovery, local-rules-discovery, worktree-isolation, generate-tests, multi-repo-feature, code-review
decisions/      lightweight ADRs for hard-to-reverse choices (+ _TEMPLATE.md)
scripts/        helpers: extract_jira_pdf_text.py (PDF), extract_jira_docx_text.py (DOCX)
```

## Profile knobs (the things you tune)

| Key | Effect |
|---|---|
| `areas` | `[backend]` / `[frontend]` / `[backend, frontend]` — which part(s) the job touches. Selects analyst role(s) + rules; for both, `plan` makes per-area slices (backend contract first). |
| `stages` | Ordered stage modules to run. |
| `design_input` | `none` / `auto` / `figma` / `screenshots` — gates the `design-analysis` stage. `auto` runs it only if a design was actually provided (design is optional). |
| `tests` | Kinds to write: `unit`, `api`, `component`, `integration`. `[]` = write none. |
| `review_passes` | Number of review rounds (1 → many). |
| `reviewers` | Lenses per round: `self`, `security`, `architecture`, `performance`. |
| `clarify_depth` | How hard the grill is: `deep` (full design-tree grill + terminology + ADRs), `light` (blocking ambiguities only), `none` (skip — omit `clarify` from `stages`). |
| `dev_review` | `true`/`false`. `true` runs the `tech-review` stage (clarify→plan) that posts the technical approach and asks for a **developer comment** before planning. |
| `isolation` | `worktree`/`in-place`. `worktree` gives each affected repo its own git worktree (own dir + branch) so runs never collide; worktrees are **kept** for later bugfix (manual cleanup). See `skills/worktree-isolation.md`. |
| `delivery` | `dual-branch`/`single-branch`. `dual-branch` = author on the releasable worktree, merge into the integration worktree (resolve conflicts), then open the **integration PR first, then the releasable PR** (each its own approval, all logged to Jira). See `adapters/bitbucket.md`. |
| `adapters` | Active integrations: `jira`, `bitbucket`, `jenkins`. `[]` = none. |
| `approval_gates` | Where to stop for approval: `after_clarify`, `after_plan`, `before_pr`, … (the `after_triage` stop is always on). |

## How to … (handing this to another team)

- **Add a profile:** copy `profiles/backend-feature.md`, edit the frontmatter knobs and the notes.
  No other file changes needed — the orchestrator reads the frontmatter.
- **Change review depth for a job type:** edit that profile's `review_passes` / `reviewers`.
- **Change grill depth for a job type:** edit `clarify_depth` (`deep`/`light`/`none`).
- **Handle a job touching both backend and frontend:** triage recommends `fullstack-feature`
  (`areas: [backend, frontend]`); `plan` makes per-area slices, backend contract first.
- **Make a repo write no tests:** set `tests: []` in the profile it uses (or a repo-local override).
- **Edit a step's behavior:** change the one file in `stages/` — every profile using it updates.
- **Add a role:** drop a file in `roles/` and reference it from the relevant stage.
- **Add an integration:** add a file in `adapters/`, document its enable/fallback behavior, and list
  its name in the profiles that should use it. Keep all secrets in env/runtime config.
- **Override per repo:** add a nested `AGENTS.md` or `.agents/profile.md` in a sub-module; the
  closest file wins.
- **Add repo-local rules a team must follow:** drop them in that repo (`.cursor/rules/*.mdc`,
  `.cursor/skills/*/SKILL.md`, `AGENTS.md`, `CLAUDE.md`, or `docs/*.md`). `load-context` auto-discovers
  and loads them before any edit, and they take precedence over the root `.agents/` defaults.

## Tool wiring

- **Codex / Cursor / others:** read root `AGENTS.md` natively.
- **Claude Code:** reads `CLAUDE.md`, which imports `@AGENTS.md`.
- **Cursor skills/rules:** symlink `.cursor/skills → ../.agents/skills` and
  `.cursor/rules → ../.agents/rules` to avoid per-tool drift; keep service-local `.cursor/rules/*.mdc`
  only as nested overrides.

## Provenance

Consolidated from the previous Codex-only `.codex/` workflow and the per-service Cursor `.cursor/`
skills/rules into this single tool-agnostic core.
