# Codex Workflow Prompts

## Jira Analysis

Analyze this Jira by reading summary, description, and attachments first without asking for approval. Extract acceptance criteria, target behavior, scope, out-of-scope areas, ambiguity, affected services/modules, proposed subtasks, and test scenarios. Do not implement yet.

## Grill-Me

Grill this plan before implementation. Ask one implementation-impacting question at a time. For each question, include your recommended answer. Do not ask anything that can be discovered from the repo.

## Jira Comment

Create or update a single Jira comment titled Codex Development Log. Use Jira wiki markup, not GitHub Markdown: h2/h3 headers, Jira tables, numbered lists, and compact bullets. Preserve the codex-development-log:v1 marker so the comment can be updated later.

## Approval Gate

After Jira intake, Grill-Me decisions, technical plan, and Jira Development Log are complete, stop and wait for explicit user approval before implementation. Do not start code changes from the planning/comment stage unless the user explicitly approves implementation.

## Implementation

Implement only after explicit user approval. Implement only the approved subtask in the affected module. Read existing patterns first, make the smallest safe change, add or update tests, and avoid unrelated refactors. If a blocker or implementation-impacting ambiguity appears, stop implementation and return to Grill-Me with one concrete question and a recommended answer.

## Self Review

Review the diff like a production reviewer. List findings first by severity with file/line references. Focus on bugs, regressions, missing tests, acceptance-criteria drift, and unnecessary changes.

## PR Description

Prepare a Bitbucket PR description with Jira key, behavior summary, changed areas, test commands and results, known risks, and QA handoff notes. Ask for user approval before opening the PR.

## Jenkins Failure Analysis

Analyze the Jenkins result. Classify the failure as compile, test, dependency, Sonar, Fortify, packaging, or deploy. Identify the shortest safe fix path and update the Jira Development Log.
