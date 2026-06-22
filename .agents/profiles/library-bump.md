---
name: library-bump
description: Dependency/library version bump with no behavior change. No new tests, single light review.
areas: [backend]
design_input: none
stages: [intake, load-context, plan, implement, test, review, handoff]
tests: []
review_passes: 1
reviewers: [self]
clarify_depth: none
dev_review: false
isolation: worktree
delivery: dual-branch
adapters: [jira, bitbucket, jenkins]
approval_gates: [after_plan, before_pr]
---

# Profile: Library Bump  *(example stub — tune as needed)*

For dependency/version bumps that don't change behavior. Demonstrates a job that **writes no tests**
and skips the `clarify` gate (there is rarely product ambiguity in a version bump).

## How the knobs apply

- **`tests: []`** → the `test` stage is a no-op (it only *runs* existing tests / builds; it writes
  none). State this in the report.
- **No `clarify` stage** → version bumps are evidence-driven; if a breaking change surfaces, the
  `implement` stage routes back to `clarify` ad hoc.
- **`review_passes: 1`, `reviewers: [self]`** → one light review focused on compatibility.
- **`adapters: [jira, bitbucket, jenkins]`** → CI is the real validation for a bump; watch it closely.

## Notes

- The point of validation here is the **build + existing test suite + CI**, not new tests.
- For a shared lib consumed by many modules, verify representative consumers build
  (`.agents/skills/multi-repo-feature.md`).
