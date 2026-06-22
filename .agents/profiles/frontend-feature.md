---
name: frontend-feature
description: Frontend/UI change (Angular). Design analysis runs only if a design is actually provided. Writes unit + component tests, one review pass.
areas: [frontend]
design_input: auto
stages: [intake, load-context, design-analysis, clarify, tech-review, plan, implement, test, review, handoff]
tests: [unit, component]
review_passes: 1
reviewers: [self]
clarify_depth: deep
dev_review: true
isolation: worktree
delivery: dual-branch
adapters: [jira, bitbucket]
approval_gates: [after_clarify, after_tech_review, after_plan, before_pr]
---

# Profile: Frontend Feature

For UI changes in the Angular apps. A visual design **may or may not** exist — design is optional, not
required. When a design is provided this profile demonstrates the design-tool path; when it isn't, the
job proceeds on requirements alone (like the backend profile).

## How the knobs apply

- **`design_input: auto`** → at `intake` the agent detects whether a design artifact was provided
  (Figma link, exported frames, or screenshot images). If yes → the `design-analysis` stage runs using
  `.agents/roles/frontend-analyst.md` to turn it into a buildable UI spec. If no → `design-analysis`
  self-skips with an explicit note and the flow continues normally. (Set `design_input: figma` or
  `screenshots` instead to *require* a design from that source.)
- **`stages` includes `design-analysis`** (between intake and clarify) — but it only executes when a
  design is actually present.
- **`tests: [unit, component]`** → unit tests plus Jasmine/Karma `*.spec.ts` component tests.
- **`review_passes: 1` with `reviewers: [self]`** → a single self-review pass (lighter than backend).
- **`adapters: [jira, bitbucket]`** → reads the issue and opens a PR; **no Jenkins** here (CI handled
  by the frontend pipeline / the user).
- **`approval_gates`** → stop after clarify, after plan, before PR.

## Notes

- Apply `.agents/rules/angular-frontend.md`. Reuse existing components before creating new ones.
- A design is optional. Provide a Figma link or screenshots to drive `design-analysis`; omit them for
  a design-less change (bugfix, validation/text tweak, behavior change) and the stage is skipped.
