---
name: hotfix
description: Urgent production fix, minimal ceremony. Unit test for the fix, single fast review.
areas: [backend]
design_input: none
stages: [intake, load-context, clarify, plan, implement, test, review, handoff]
tests: [unit]
review_passes: 1
reviewers: [self]
clarify_depth: light
dev_review: false
isolation: worktree
delivery: dual-branch
ci_fix_attempts: 2
adapters: [jira, bitbucket, jenkins]
approval_gates: [after_plan, before_pr]
---

# Profile: Hotfix  *(example stub — tune as needed)*

For urgent production fixes. Demonstrates the **fast path**: the same stages but the lightest review
(`review_passes: 1`) and a focused single test for the fix.

## How the knobs apply

- **`tests: [unit]`** → write a regression test that fails before the fix and passes after; skip the
  broader API/component suites for speed.
- **`review_passes: 1`, `reviewers: [self]`** → one quick correctness pass.
- **`approval_gates: [after_plan, before_pr]`** → keeps the plan and PR gates (you still don't ship
  unreviewed), but `clarify` stays a stage rather than a hard gate so a clearly-scoped fix moves fast.

## Notes

- `areas` defaults to `[backend]` but is **tunable per incident** — set `[frontend]` or
  `[backend, frontend]` at triage if the fix lives there. `clarify_depth: light` keeps it fast.
- Keep the change minimal and targeted at the regression. Don't bundle unrelated fixes.
- After shipping, consider a follow-up job with a fuller profile if the root cause needs broader work.
