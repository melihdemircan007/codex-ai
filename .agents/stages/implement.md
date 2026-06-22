# Stage: Implement

**Role:** adopt `.agents/roles/implementer.md`.
**Precondition:** the `after_plan` gate was approved.

## Precondition — work in the job's worktree (when `isolation: worktree`)

If the profile sets `isolation: worktree`, make all edits/builds/tests **inside the job's git worktree**
for the target repo (`.agents/skills/worktree-isolation.md`) — never in the main checkout. Worktrees are
kept afterward (manual cleanup only).

For `delivery: dual-branch`, **author the code in the `…-releasable` worktree** (`feature/<BRANCH>-releasable`).
Leave the `…-integration` worktree untouched until `handoff` (it receives the merge there). One worktree
pair per affected nested repo.

## Precondition — repo-local guidance loaded

Before writing code in **any** repo, confirm `load-context` has loaded that repo's local guidance. If
it hasn't (e.g. you jumped straight here), load it now via `.agents/skills/local-rules-discovery.md` and
**follow it** — it takes precedence over root defaults. Example: in `ecom-admin-client` you must follow
its `AGENTS.md` (Angular 6, no tests, no new patterns) and `docs/yeni-ekran-sablonu.md` golden-standard
screen template before touching code.

## Rules

- Implement the approved execution slices, one focused deliverable at a time.
- Read existing patterns first; follow them. Apply the **repo-local** rules loaded by `load-context`,
  then the relevant root rules: `.agents/rules/java-backend.md` (Spring) or
  `.agents/rules/angular-frontend.md` (UI). Local rules win on conflict.
- Make the **smallest safe change**. No unrelated refactors.
- **Honor the Decision Checklist + Must-Not-Exist list** (`.agents/rules/requirement-traceability.md`):
  build every confirmed item, **never** build a Must-Not item, and **never** reintroduce a `superseded`
  decision (e.g. don't add a *Clear* button that a later decision removed).
- Write or update tests **with** the code — but only the kinds in the profile's `tests` knob. The
  dedicated `test` stage formalizes/extends them; if `tests: []`, write none and say so.
- Continue autonomously through the approved slices. **Do not commit or push** without approval.
- If a blocker or new implementation-impacting ambiguity appears, **return to `clarify`** and ask one
  concrete question with a recommended answer — do not guess.

## Output

The code changes for the approved slices, plus a brief note of what changed and any new risk that
appeared during implementation.
