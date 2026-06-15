# Codex Workspace Instructions

This workspace uses the Codex agentic development workflow documented in `.codex/workflows/agentic-development-workflow.md`.

## Default Operating Model

- Work from Jira summary, description, and attachments first; read these automatically during Jira intake without asking for approval.
- Use controlled autonomy: analyze, grill, plan, and update the Jira Development Log; wait for user approval before starting implementation.
- During implementation, continue autonomously unless blocked; if an implementation-impacting ambiguity appears, return to the Grill-Me Gate and ask the user.
- Ask before opening PRs, rerunning Jenkins, merging, or handing off to QA.
- Before implementation, run the Grill-Me Gate to close important ambiguity.
- Keep one Jira comment updated as the source of truth for plan, progress, tests, review notes, PR/Jenkins status, and QA handoff.
- Default to internal execution slices instead of physical Jira sub-tasks.
- Recommend physical Jira sub-tasks only when multiple people/teams, multiple PRs, independent deliverables, separate QA/DevOps tracking, or risky rollout tracking is needed.
- Do not store Jira, Bitbucket, Jenkins, or other tokens in repo files or chat-visible logs.

## Verification Defaults

- Run targeted tests for changed behavior.
- Run the affected module build before PR handoff.
- For Maven modules, prefer `mvn test`; use `mvn clean verify` when integration/failsafe checks matter.
- For Gradle modules, prefer `./gradlew test`, then `./gradlew build` before PR handoff.
- For frontend modules, run available `npm test`, `npm run lint`, and `npm run build` scripts.
