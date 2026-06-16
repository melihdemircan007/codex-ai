# Codex Workspace Instructions

## Mandatory First Step For Jira Work

- Before any Jira-based workflow or Jira MCP read, first check that both `JIRA_BASE_URL` and `JIRA_PERSONAL_TOKEN` are present in the environment without printing their values.
- If either variable is missing, stop immediately and ask the user to define the missing variable(s).
- Do not read Jira data, Jira attachments, Jira comments, repo implementation context, or start planning for that Jira until the user confirms both variables are available.

This workspace uses the Codex agentic development workflow documented in `.codex/workflows/agentic-development-workflow.md`.

## Default Operating Model

- Work from Jira summary, description, and attachments first; read these automatically during Jira intake without asking for approval.
- For Jira intake via Atlassian MCP, do not repeat tool discovery when the known tools are available: `jira_get_issue`, `jira_download_attachments`; Jira comments are read through `jira_get_issue(comment_limit=...)`, and comment create/update uses Jira REST fallback when MCP write tools are not exposed.
- Use controlled autonomy: analyze, grill, plan, and update the Jira Development Log; wait for user approval before starting implementation.
- During implementation, continue autonomously unless blocked; if an implementation-impacting ambiguity appears, return to the Grill-Me Gate and ask the user.
- Ask before opening PRs, rerunning Jenkins, merging, or handing off to QA.
- Before implementation, run the Grill-Me Gate as a visible checkpoint in chat and wait for the user's explicit response before moving to the Technical Plan. List previous decisions only from the active `Codex Development Log` Jira comment or the current chat session; ignore changelog-only, deleted, or historical comment bodies as decision sources.
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
