---
name: fullstack-feature
description: Feature touching BOTH backend and frontend (e.g. admin API + Angular UI). Per-area slices, backend contract first, unit+api+component tests, two review passes.
areas: [backend, frontend]
design_input: auto
stages: [intake, load-context, design-analysis, clarify, tech-review, plan, implement, test, review, handoff]
tests: [unit, api, component]
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

# Profile: Full-Stack Feature

For work that spans **server and UI** together — the common case where one feature needs an API/proxy
change in a backend service *and* a screen change in an Angular app.

## How the knobs apply

- **`areas: [backend, frontend]`** → `intake`/`clarify`/`plan` use **both** `backend-analyst` and
  `frontend-analyst`, applying both `.agents/rules/java-backend.md` and `.agents/rules/angular-frontend.md`.
- **`plan` produces per-area execution slices** and sequences them **backend contract first, then
  frontend** (so the UI builds against a settled API). Follow `.agents/skills/multi-repo-feature.md` for
  dependency ordering: one feature branch per affected repo, **one** dev log, **one** coordinated PR cycle.
- **`design_input: auto`** → `design-analysis` runs only if a design was actually provided; the frontend
  slice proceeds on requirements alone otherwise.
- **`tests: [unit, api, component]`** → backend unit+API tests *and* frontend component tests.
- **`review_passes: 2`, `reviewers: [self, security]`** → two rounds across both areas.
- **`clarify_depth: deep`** → full grill across both areas before planning.
- **`adapters: [jira, bitbucket, jenkins]`** → issue intake, PR per repo, CI watched (each behind its gate).

## Notes

- Keep the API contract and the UI consumption consistent — the clarify gate should pin down the
  contract (paths, DTOs, status codes) before the frontend slice starts.
- If the job turns out to touch only one area after intake, switch to `backend-feature` /
  `frontend-feature` rather than carrying empty slices.
