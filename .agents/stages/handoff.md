# Stage: Handoff

**Goal:** Package the work for PR, CI, and QA. Every outward-facing action here needs its own approval.

## Done = fully traced (precondition)

Before any PR/handoff, confirm **full requirement traceability**
(`.agents/rules/requirement-traceability.md`): every Decision Checklist item met with code evidence,
every Must-Not-Exist item verified absent, no `superseded` decision reintroduced. **If a single item is
unmet or contradicted, the job is NOT done** — report the gap instead of handing off.

## PR (only if `bitbucket` in `adapters`)

Follow `.agents/adapters/bitbucket.md`. Verify the PR-readiness checklist, prepare a description
(issue key, behavior summary, changed areas, test commands+results, risks, QA notes), then **ask for
explicit approval before pushing branches or opening the PR**. If `bitbucket` is not enabled, instead
produce the same summary as text for the user to use manually.

### Dual-branch delivery (when `delivery: dual-branch`)

Run the bitbucket adapter's **Delivery model** sequence:
1. Code is already authored + tested in the **releasable** worktree.
2. In the **integration** worktree, `git merge feature/<BRANCH>-releasable`, **resolve conflicts**, build/test.
3. Auth preflight → push both branches.
4. **STOP for approval, then open PR #1 → integration.**
5. **STOP for approval, then open PR #2 → releasable.**

After each step, **append to the Jira dev log** (Delivery block + Work Done rows): both branch names,
integration merge/conflict status, Integration PR link, Releasable PR link, in order. Two PR approval
stops — integration first, then releasable.

## CI (only if `jenkins` in `adapters`)

Follow `.agents/adapters/jenkins.md`: after PR approval, check the build and classify any failure
(compile / test / dependency / Sonar / Fortify / packaging / deploy). Don't merge without approval.

## QA handoff

Prepare QA notes regardless of adapters:
- Acceptance criteria restated as **testable scenarios** (include negative/edge cases when behavior changed).
- Changed service/module + risky areas.
- Test data requirements.
- PR link + CI status (if available).
- Known limitations / deferred items.

## Worktrees are kept

If `isolation: worktree`, **do not remove** the job's worktrees at handoff — they're kept so you can
return and fix a bug from where the work was done. List them with `git worktree list`; the user removes
them manually when truly done (`.agents/skills/worktree-isolation.md`).

## Output

The PR description + QA handoff notes. This stage contains the `before_pr` gate (and any merge/QA
gate). STOP at each outward-facing action and wait for explicit approval.
