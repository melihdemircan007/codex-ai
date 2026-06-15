# Codex Agentic Development Workflow

## Goal

Standardize how Codex supports Jira-based development from acceptance criteria analysis through implementation, tests, self-review, Bitbucket PR, Jenkins validation, and QA handoff.

## Workflow Stages

1. Jira Intake
   - Read Jira summary, description, and all attachments automatically; do not ask for approval for these reads.
   - Treat attachments as first-class requirements sources, especially PDFs, images, spreadsheets, and analysis documents.
   - Extract acceptance criteria from summary, description, and attachments; if Jira fields are sparse, inspect attachments before asking the user.
   - Use comments or linked issues only when acceptance criteria are ambiguous or explicitly reference them.
   - Identify affected service/module, expected behavior, scope boundaries, and likely test impact.

2. Grill-Me Gate
   - Before coding, ask one critical question at a time when product or technical intent is unclear.
   - Provide a recommended answer for each question.
   - Never ask questions that can be answered by reading the repo, configs, tests, Jenkinsfile, or existing patterns.
   - Stop grilling when the user says to wrap up, proceed, or when all implementation-impacting ambiguity is closed.

3. Technical Plan
   - Break the work into internal execution slices by deliverable or behavior, not by individual files.
   - Use execution slices such as Backend API, Admin Backend Proxy, Frontend UI, Validation, Permission/Config, Tests, Self Review, PR/Jenkins, and QA Handoff when they fit the Jira.
   - For each execution slice, capture changed behavior, files/modules likely affected, tests to add/update, risks, and acceptance criteria coverage.
   - Default to keeping one Jira issue and one Jira Development Log; do not create physical Jira sub-tasks by default.
   - Recommend physical Jira sub-tasks only when the work needs multiple people/teams, multiple PRs, independent deliverables, separate QA/DevOps tracking, or risky rollout tracking.
   - Prefer the smallest change that satisfies the acceptance criteria.

4. Jira Single Comment Log
   - Create or update one Jira comment titled `Codex Development Log`.
   - Do not create progress-comment spam.
   - Format the comment with Jira wiki markup: `h2.`, `h3.`, Jira tables, numbered lists, and compact bullets.
   - Include the internal execution slices and the physical Jira sub-task decision in the comment.
   - Update the same comment after planning, implementation, test execution, self-review, PR creation, Jenkins result, and QA handoff.
   - Use the Jira wiki template in `.codex/templates/jira-development-log.jira`.

5. Approval Gate
   - After Jira intake, Grill-Me decisions, technical plan, and Jira Development Log are complete, stop and wait for explicit user approval before implementation.
   - Do not start code changes from the planning/comment stage unless the user explicitly approves implementation.

6. Implementation
   - Follow existing code style and module patterns.
   - Avoid unrelated refactors.
   - Write or update tests with the code change.
   - Implement the approved execution slices; keep each slice focused on one deliverable or behavior.
   - Continue autonomously through code, tests, and self-review once implementation is approved.
   - If a blocker or implementation-impacting ambiguity appears, return to the Grill-Me Gate and ask the user one concrete question with a recommended answer.
   - Keep external-system actions under user approval: PR open, Jenkins rerun, merge, and QA handoff.

7. Self Review
   - Review the diff as a production reviewer.
   - Prioritize bugs, regressions, missing tests, behavioral drift from acceptance criteria, and unnecessary changes.
   - Fix valid findings before PR handoff.

8. PR Handoff
   - Prepare a Bitbucket PR summary with Jira key, behavior summary, test evidence, risks, and QA notes.
   - Link the PR in the Jira Development Log.
   - Use the checklist in `.codex/checklists/pr-readiness.md`.

9. Jenkins and QA
   - Check Jenkins after PR approval or when the user asks.
   - Classify failures as compile, test, dependency, Sonar, Fortify, packaging, or deploy.
   - If Jenkins passes, prepare QA handoff notes from acceptance criteria and risk areas.

## Quality Gate Defaults

- Targeted tests for changed behavior are required before module build.
- Affected module build is required before PR handoff unless blocked by environment or dependency access.
- Full workspace build is not the default in this multi-service workspace.
- Shared library changes require at least one representative consumer module build when feasible.

## Security Rules

- Do not write Jira, Bitbucket, Jenkins, Sonar, Fortify, Maven, Gradle, npm, or registry tokens into repo files.
- Prefer environment variables, secret managers, MCP headers managed outside the repo, or approved local config.
- If a token is exposed in chat or logs, recommend revocation/rotation.
