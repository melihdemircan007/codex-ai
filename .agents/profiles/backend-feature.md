---
name: backend-feature
description: Backend service/API change (Java/Spring). No visual design input. Writes unit + API tests, two review passes.
areas: [backend]
design_input: none
stages: [intake, load-context, clarify, tech-review, plan, implement, test, review, handoff]
tests: [unit, api]
review_passes: 2
reviewers: [self, security]
clarify_depth: deep
dev_review: true
isolation: worktree
delivery: dual-branch
ci_fix_attempts: 2
adapters: [jira, bitbucket, jenkins]
approval_gates: [after_clarify, after_tech_review, after_plan, before_pr]
---

# Profile: Backend Feature

For changes to Spring Boot services / BFFs where the contract comes from an analysis document and
existing repo conventions — **there is no design/Figma input**.

## How the knobs apply

- **Analyst:** `intake`/`clarify`/`plan` use `.agents/roles/backend-analyst.md`.
- **`design_input: none`** → the `design-analysis` stage does not run.
- **`tests: [unit, api]`** → the `test` stage writes JUnit unit tests *and* endpoint/contract tests.
- **`review_passes: 2` with `reviewers: [self, security]`** → two review rounds, each applying the
  self and security lenses; fix findings between rounds.
- **`adapters: [jira, bitbucket, jenkins]`** → intake reads the Jira issue, handoff opens a Bitbucket
  PR and watches Jenkins (each behind its own approval).
- **`approval_gates`** → stop after clarify, after plan, and before opening the PR.

## Notes

- Apply `.agents/rules/java-backend.md` and `.agents/rules/testing-standards.md`.
- For changes spanning shared libs + consumers, use `.agents/skills/multi-repo-feature.md`.
