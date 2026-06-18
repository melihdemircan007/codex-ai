# Codex Workflow Prompts

## Jira Analysis

Analyze this Jira by reading summary, description, and attachments first without asking for approval. Use known Atlassian MCP tools directly when available: `jira_get_issue` for issue fields/comments via `comment_limit`/attachment metadata and `jira_download_attachments` for attachment content. Do not repeat MCP tool discovery unless the known calls fail. Extract acceptance criteria, target behavior, scope, out-of-scope areas, ambiguity, affected services/modules, internal execution slices, the physical Jira sub-task decision, and test scenarios. Do not implement yet.

## Jira MCP Intake

Use `jira_get_issue` first for summary, description, comments via `comment_limit`, status, issue type, priority, assignee, reporter, labels, components, fix versions, and attachment metadata. Use `jira_download_attachments` second only when attachments exist. For Jira Development Log comments, read active comments with `jira_get_issue(comment_limit=...)` and locate `codex-development-log:v1`; ignore deleted, historical, and changelog-only bodies. If MCP comment write/update tools are not exposed, use Jira REST fallback: `POST /rest/api/2/issue/{issueKey}/comment` and `PUT /rest/api/2/issue/{issueKey}/comment/{commentId}`. Do not print MCP headers, tokens, or raw secret config values.

## Execution Slice Decision

Break the work into internal execution slices by deliverable or behavior, not by individual files. Default to no physical Jira sub-tasks. Recommend physical Jira sub-tasks only when multiple people/teams, multiple PRs, independent deliverables, separate QA/DevOps tracking, or risky rollout tracking is needed.

## Grill-Me

Run Grill-Me as a visible checkpoint after Jira Intake and before Technical Plan, then wait for the user's explicit response before proceeding. Previous decisions may be listed only when they exist in the currently active `Codex Development Log` Jira comment or were explicitly made in the current chat session. Ignore Jira changelog entries, deleted comments, historical comment bodies, and MCP changelog-only text as decision sources. If previous decisions exist, list them and ask the user whether to reuse them before marking them as reused. Then check whether any new implementation-impacting ambiguity remains after Jira summary, description, attachments, and active comments are reviewed. Review repo patterns only when creating a new technical plan, when the Jira or active Development Log explicitly references code-level uncertainty, or when the user asks for repo/code validation. If ambiguity remains, ask one implementation-impacting question at a time and include your recommended answer. If multiple recommendations are pending user confirmation, never ask for bulk approval; ask the first pending recommendation as one concrete question, wait for the user's answer, record that answer as that item's final decision, then ask the next pending recommendation. If no ambiguity remains, explicitly write `No new implementation-impacting ambiguity found`, but still wait for the user's explicit confirmation before moving to Technical Plan. Do not move to Technical Plan while any recommended decision remains unanswered. Do not ask anything that can be discovered from the already-reviewed active sources.

## Jira Comment

Create or update a single Jira comment titled Codex Development Log. Read active comments with `jira_get_issue(comment_limit=...)` and update the newest active comment containing `codex-development-log:v1`; create a new comment only if no active comment has the marker. Do not infer an active log from deleted, historical, or changelog-only bodies. When the user asks to work on the active Development Log, read and update that active log first; do not announce or start a repo/code-structure compatibility check unless explicitly requested or required by the active log. Use Jira wiki markup, not GitHub Markdown: h2/h3 headers, Jira tables, numbered lists, and compact bullets. Include internal execution slices and the physical Jira sub-task decision. Preserve the `codex-development-log:v1` marker so the comment can be updated later.

## Approval Gate

After Jira intake, Grill-Me decisions, technical plan, Jira Development Log, and local branch preparation are complete, stop and wait for explicit user approval before implementation. Do not start code changes from the planning/comment stage unless the user explicitly approves implementation. Implementation approval is not approval to commit, push, open PRs, rerun Jenkins, merge, or hand off to QA.

## Branch Preparation Gate

Before implementation approval, prepare local branches in every repo where code will be written. Derive `BRANCH_NAME` from Jira key plus sanitized Jira summary. Fetch remote refs, verify `origin/releasable` and `origin/integration`, then create `feature/${BRANCH_NAME}-releasable` from `origin/releasable` and `feature/${BRANCH_NAME}-integration` from `origin/integration`. Do not commit, push, open PRs, rerun Jenkins, merge, or hand off to QA during branch preparation. Record branch names and base refs in the Jira Development Log.

## Implementation

Implement only after explicit user approval and after the releasable/integration local branches are prepared. Implement the approved execution slice in the affected module. Read existing patterns first, make the smallest safe change, add or update tests, and avoid unrelated refactors. If a blocker or implementation-impacting ambiguity appears, stop implementation and return to Grill-Me with one concrete question and a recommended answer. Do not commit or push without explicit user approval.

## Self Review

Review the diff like a production reviewer. List findings first by severity with file/line references. Focus on bugs, regressions, missing tests, acceptance-criteria drift, and unnecessary changes.

## PR Description

Prepare a Bitbucket PR description with Jira key, behavior summary, changed areas, test commands and results, known risks, and QA handoff notes. Ask for user approval before opening the PR.

## Jenkins Failure Analysis

Analyze the Jenkins result. Classify the failure as compile, test, dependency, Sonar, Fortify, packaging, or deploy. Identify the shortest safe fix path and update the Jira Development Log.
