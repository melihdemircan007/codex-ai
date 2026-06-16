# Codex Agentic Development Workflow

## Goal

Standardize how Codex supports Jira-based development from acceptance criteria analysis through implementation, tests, self-review, Bitbucket PR, Jenkins validation, and QA handoff.

## Workflow Stages

1. Jira Intake
   - Before starting any Jira-based workflow, run a Jira credential preflight by checking that both `JIRA_BASE_URL` and `JIRA_PERSONAL_TOKEN` are present in the environment without printing their values.
   - If either `JIRA_BASE_URL` or `JIRA_PERSONAL_TOKEN` is missing, stop the workflow before Jira intake, ask the user to define the missing environment variable(s), and do not read Jira data, attachments, comments, or repo implementation context for that Jira until the user confirms the variables are available.
   - Read Jira summary, description, and all attachments automatically; do not ask for approval for these reads.
   - Use known Atlassian MCP tools directly when available; do not spend time rediscovering them on every Jira.
   - Known Jira MCP read tools: `jira_get_issue` for summary, description, comments via `comment_limit`, status, and attachment metadata. Use `jira_download_attachments` only as a fallback for attachment content when direct URL download or local files are unavailable.
   - Treat attachments as first-class requirements sources, especially PDFs, images, spreadsheets, and analysis documents.
   - When Jira attachment metadata includes a PDF (`application/pdf` or `.pdf` filename), create a local PDF copy and extract readable text with available deterministic tools before Grill-Me Gate.
   - Prefer direct attachment URL/local-file intake using Jira metadata when available. This avoids emitting large MCP embedded/base64 PDF blobs into the chat/tool transcript.
   - Use Jira credentials only from environment variables (`JIRA_PERSONAL_TOKEN`, `JIRA_BASE_URL`) or Codex-owned MCP config explicitly used for attachment retrieval; never print token values or raw config headers.
   - If direct download is unavailable and `jira_download_attachments` returns an embedded/base64 resource instead of a local file, do not treat the PDF as analyzed until a deterministic extractor has produced readable text. If the extractor reports no readable text, explicitly record that OCR/manual inspection is required.
   - Extract acceptance criteria from summary, description, and attachments; if Jira fields are sparse, inspect attachments before asking the user.
   - Use comments or linked issues only when acceptance criteria are ambiguous or explicitly reference them.
   - Identify affected service/module, expected behavior, scope boundaries, and likely test impact.

2. Grill-Me Gate
   - Always run this as a visible checkpoint after Jira Intake and before Technical Plan.
   - Never leave the Grill-Me Gate silently. Always show the Grill-Me checkpoint to the user in chat and require an explicit user response before moving to the Technical Plan.
   - Treat previous Grill-Me decisions as existing only when they are present in the currently active `Codex Development Log` Jira comment or were explicitly made in the current chat session.
   - Do not reuse Grill-Me decisions from Jira changelog entries, deleted comments, historical comment bodies, or MCP changelog-only text. Those sources may prove history existed, but they are not active decisions.
   - Do not inspect old/historical Development Log bodies in Jira changelog entries to check whether a decision was "definitely written somewhere". If a decision is absent from the active Development Log and current chat, treat it as unconfirmed and ask at the Grill-Me Gate.
   - Never claim a decision is in Jira or confirmed because it appears in all/most historical Development Log snapshots. Historical consistency is not confirmation; only the active Development Log, current chat, Jira summary/description/attachments, or repo evidence can confirm a decision.
   - If previous Grill-Me decisions exist in the active log or current chat session, list them first and ask the user whether to reuse them before marking them as reused decisions.
   - Check whether any new implementation-impacting ambiguity remains after Jira summary, description, attachments, and comments are reviewed.
   - Review repo patterns during Grill-Me only when creating a new technical plan, when the Jira or active Development Log explicitly references code-level uncertainty, or when the user asks for repo/code validation.
   - Treat any implementation choice that changes behavior, permissions, API contract, persistence rules, rollout, ownership, QA expectations, or user-visible navigation/linking as an implementation-impacting decision unless the Jira or existing repo pattern already fixes it unambiguously.
   - Even when Jira evidence or repo patterns fix a user-visible value unambiguously, explicitly show the concrete value in the Grill-Me Decision Ledger. This includes client routes/URLs, menu labels, API paths, permission keys, feature names, and external handoff names. Do not hide these under a generic "repo pattern applies" statement.
   - First list `Discovered Decisions`: decisions Codex found from Jira summary/description, attachments, active Jira comments, repo code, configs, tests, or established patterns. Number them sequentially and show the source/evidence for each decision.
   - After listing Discovered Decisions, wait for the user to approve or edit them before asking new open questions. The user may reference decisions by number, including compact inputs such as `1`, `4`, or `2 and 5`; update only those numbered decisions and keep their approval/edit evidence.
   - Do not proceed from Discovered Decisions to open Grill-Me questions while any discovered decision is still unapproved or being edited.
   - If ambiguity remains, ask one critical question at a time and include a recommended answer for each question.
   - A recommended answer is only a recommendation; never record it as `Final Decision`, Jira log decision, or plan assumption until the user explicitly approves it or the decision is proven by existing repo/Jira evidence.
   - For every Grill-Me question or proposed decision, keep an auditable record with these separate fields: the exact question/decision topic, Codex recommended answer, user approval evidence from the current chat or active log, final decision, and status.
   - When a user approves or changes a recommendation, record the user approval evidence in concise natural language such as `User approved in chat: "..."` or `User changed decision in chat: "..."`. Do not hide approval evidence inside a generic confirmed-decisions paragraph.
   - After all Discovered Decisions are approved or edited, list `Open Decision Questions`: implementation-impacting decisions that could not be derived from Jira/repo evidence. Ask these one at a time and record the answer in a separate open-question table.
   - Do not collapse an unresolved recommended answer into `No new implementation-impacting ambiguity found`.
   - If no new ambiguity remains, explicitly record: `No new implementation-impacting ambiguity found`.
   - Before leaving the Grill-Me Gate, run a visible Decision Ledger:
     - `Confirmed decisions`: user-approved or directly proven decisions.
     - `Recommended but unconfirmed`: recommendations still waiting for user approval.
     - `No-question rationale`: why any apparent decision did not require a question, with the exact proven value listed when the decision affects user-visible navigation/linking, API contract, permissions, persistence rules, QA expectations, or rollout.
   - If `Recommended but unconfirmed` contains more than one item, do not ask for a single bulk approval. Ask the first pending recommendation as one concrete question, wait for the user's answer, record that answer as that item's `Final Decision`, then ask the next pending recommendation.
   - Do not proceed to Technical Plan while any `Recommended but unconfirmed` item is unanswered. Phrases like `proceed with the recommendations` count only after the user has explicitly answered each pending recommendation one by one.
   - Proceed to Technical Plan only after the user explicitly confirms the Grill-Me checkpoint and `Recommended but unconfirmed` is empty.
   - Never ask questions that can be answered by reading the repo, configs, tests, Jenkinsfile, or existing patterns.
   - Stop grilling when the user says to wrap up, proceed, or when all implementation-impacting ambiguity is closed.

3. Technical Plan
   - Break the work into internal execution slices by deliverable or behavior, not by individual files.
   - Use execution slices such as Backend API, Admin Backend Proxy, Frontend UI, Validation, Permission/Config, Tests, Self Review, PR/Jenkins, and QA Handoff when they fit the Jira.
   - For each execution slice, capture changed behavior, files/modules likely affected, tests to add/update, risks, and acceptance criteria coverage.
   - Link plan assumptions back to Confirmed decisions or repo/Jira evidence. Do not introduce new unconfirmed implementation choices in the Technical Plan; return to the Grill-Me Gate if one appears.
   - Default to keeping one Jira issue and one Jira Development Log; do not create physical Jira sub-tasks by default.
   - Recommend physical Jira sub-tasks only when the work needs multiple people/teams, multiple PRs, independent deliverables, separate QA/DevOps tracking, or risky rollout tracking.
   - Prefer the smallest change that satisfies the acceptance criteria.

4. Jira Single Comment Log
   - Create or update one Jira comment titled `Codex Development Log`.
   - Read existing comments with `jira_get_issue(comment_limit=...)` and find the `codex-development-log:v1` marker before creating a new comment.
   - Only treat currently active Jira comments as existing Development Logs. Ignore deleted, historical, or changelog-only comment bodies, even if they contain `codex-development-log:v1`.
   - Only the active Development Log can be used as the Jira source for previous Grill-Me decisions. Changelog-only Development Log bodies must not be copied into the active log as confirmed/reused decisions unless the user explicitly reconfirms them in chat.
   - Do not mine changelog-only Development Log bodies for missing endpoint names, routes, permission keys, API contracts, persistence rules, or other implementation-impacting decisions. If those values are not in the active log/current chat or directly proven by Jira attachments/repo evidence, record them as pending Grill-Me questions.
   - If multiple active Development Log comments exist, update the newest active one and ignore older duplicates unless the user explicitly asks to clean them up.
   - When the user asks to work on the active Development Log, read and update the active log first; do not announce or start a repo/code-structure compatibility check unless the user explicitly requests it or the active log requires code validation.
   - Do not create progress-comment spam.
  - Format the comment with Jira wiki markup: `h2.`, `h3.`, Jira tables, numbered lists, and compact bullets.
  - For status rows in the Work Done table, use explicit text states such as `{color:green}done{color}` and `pending` instead of literal `x`/checkbox markers; Jira may render `x` as a red cross.
  - Include the internal execution slices and the physical Jira sub-task decision in the comment.
  - In the Grill-Me section, use a `Grill-Me Discovered Decisions` table for decisions Codex found from Jira/PDF/repo evidence, with separate columns for `Decision Topic`, `Source / Evidence`, `Codex Found Decision`, `User Approval / Edit Evidence`, `Final Decision`, and `Status`.
  - In the Grill-Me section, use a separate `Grill-Me Open Questions / User Decisions` table for decisions that required a user answer, with separate columns for `Question`, `Codex Recommended Answer`, `User Answer / Evidence`, `Final Decision`, and `Status`.
  - In both Grill-Me tables, keep `User Approval / Edit Evidence` or `User Answer / Evidence` empty and `Final Decision` as `Pending user confirmation` for any decision the user has not explicitly approved or edited.
  - Keep a short `Final Grill-Me Decisions` section after both tables so reviewers can scan all approved decisions without expanding long Jira table rows.
   - Do not mark `Grill-Me completed` in the Work Done table while any Grill-Me decision is pending user confirmation.
   - Update the same comment after planning, implementation, test execution, self-review, PR creation, Jenkins result, and QA handoff.
   - If Jira MCP comment write/update tools are not exposed, use Jira REST fallback: `POST /rest/api/2/issue/{issueKey}/comment` to create and `PUT /rest/api/2/issue/{issueKey}/comment/{commentId}` to update.
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

## Jira MCP Defaults

- Prefer native exposed Jira MCP tools when the session provides them.
- If native MCP tools are not exposed, read repo-local `.codex/mcp.toml` and Codex-owned MCP configuration only; do not read Cursor MCP configuration or other IDE-specific configs.
- When a direct MCP/REST fallback is needed, use Codex-owned secret sources such as the configured `token_env` or `~/.codex/config.toml` without printing tokens.
- For Jira PDF attachment intake, use environment variables (`JIRA_PERSONAL_TOKEN`, `JIRA_BASE_URL`) instead of repo-stored tokens.
- Skip repeated `tools/list` discovery unless a known tool call fails or the MCP server changes.
- Use `jira_get_issue` first with fields for summary, description, attachment metadata, status, issue type, priority, assignee, reporter, labels, components, and fix versions; set `comment_limit` when comments are needed.
- Use `jira_get_issue(comment_limit=...)` to read active Jira comments and locate the existing `codex-development-log:v1` comment marker.
- Do not infer the active Development Log from changelog entries, deleted comment snapshots, or comment history text. Changelog data can prove that a log existed before, but it must not be updated or counted as the current source of truth.
- Do not read changelog-only historical Development Log bodies to recover or validate missing decisions. If an endpoint, route, permission key, or other implementation-impacting value is missing from the active log, ask the user instead of using historical snapshots as evidence.
- For active Development Log maintenance, prefer the active Jira comment as the source of truth and avoid repo inspection unless a new plan, explicit code validation request, or implementation step requires it.
- Use `jira_download_attachments` only after issue metadata confirms attachments exist and direct URL/local-file attachment intake is unavailable; avoid it for PDFs when it would emit embedded/base64 content into the transcript.
- Jira MCP currently exposes comment reading through `jira_get_issue`, not dedicated comment write/update tools; use Jira REST fallback for creating/updating the single development log comment when needed.
- Never log MCP headers, personal tokens, or raw secret config values.

## Quality Gate Defaults

- Targeted tests for changed behavior are required before module build.
- Affected module build is required before PR handoff unless blocked by environment or dependency access.
- Full workspace build is not the default in this multi-service workspace.
- Shared library changes require at least one representative consumer module build when feasible.

## Security Rules

- Do not write Jira, Bitbucket, Jenkins, Sonar, Fortify, Maven, Gradle, npm, or registry tokens into repo files.
- Prefer environment variables, secret managers, MCP headers managed outside the repo, or approved local config.
- If a token is exposed in chat or logs, recommend revocation/rotation.
