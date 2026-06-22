# Agent Instructions

This repository uses a **tool-agnostic, modular agentic development workflow**. It works the
same in Codex, Claude Code, Cursor, or any other AI coding agent.

## Start here

**Read and follow [`.agents/workflow.md`](.agents/workflow.md).** It is the orchestrator: it tells
you to select a *profile* for the job, load its settings, run the stages in order, and **stop for
explicit user approval at every gate**.

Before doing any work:
1. Determine the job type and select a profile from `.agents/profiles/` (ask the user if ambiguous).
2. Honor the profile's frontmatter knobs (`stages`, `tests`, `review_passes`, `adapters`, `approval_gates`).
3. Never proceed across an approval gate without an explicit "go".

## Layout

| Path | What it holds |
|---|---|
| `.agents/workflow.md` | The orchestrator loop (start here). |
| `.agents/profiles/` | Job profiles that compose stages + knobs (the things you tune per job). |
| `.agents/stages/` | Reusable workflow steps (intake, clarify, plan, implement, test, review, handoff…). |
| `.agents/roles/` | Personas a stage adopts (frontend-analyst, backend-analyst, implementer, tester, reviewer). |
| `.agents/adapters/` | Optional integrations (jira, bitbucket, jenkins) — enabled per profile. |
| `.agents/rules/` | Repo coding conventions (java-backend, angular-frontend, testing-standards). |
| `.agents/skills/` | Token-efficient how-tos (endpoint-discovery, generate-tests, multi-repo-feature, code-review). |
| `.agents/scripts/` | Helper scripts (PDF text extraction for issue attachments). |

## Repo facts

- Monorepo of ~45 modules: Java 17/Maven + Java 21/Gradle Spring Boot services, BFFs, shared libs, Angular frontends.
- Build/test: Maven → `mvn test` (`mvn clean verify` for integration); Gradle → `./gradlew test` then `./gradlew build`; frontend → `npm test`, `npm run lint`, `npm run build`.
- Default is to build/test the **affected module only**, not the whole workspace.

## Security

- Never write Jira/Bitbucket/Jenkins/registry tokens into repo files or chat.
- Jira credentials come from the environment (`JIRA_BASE_URL` / `JIRA_PERSONAL_TOKEN`), never the repo.
  Git/Bitbucket auth uses your **ambient git setup** (SSH key or OS credential helper) — the workflow
  injects no token; an adapter preflight verifies it and stops to ask if it's missing.
- Use environment variables or runtime MCP/secret config outside the repo. If a secret leaks, recommend rotation.

> Claude Code users: `CLAUDE.md` imports this file via `@AGENTS.md`. Cursor and Codex read this file directly.
