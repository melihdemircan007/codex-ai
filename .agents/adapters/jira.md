# Adapter: Jira (issue tracker)

**Optional.** Active only when a profile lists `jira` in `adapters`. If not listed, the `intake`
stage takes the requirement from the user's prompt instead and none of this runs.

## Credential preflight (mandatory before any Jira read)

- Verify `JIRA_BASE_URL` and `JIRA_PERSONAL_TOKEN` exist in the environment **without printing them**.
- If either is missing, **stop** and ask the user to set it. Do not read issues, attachments, or
  comments until both are confirmed.
- Never write tokens into repo files or chat. Use env vars / runtime MCP config only.

## Reading an issue

- Prefer Atlassian MCP tools when exposed: `jira_get_issue` (summary, description, status, attachment
  metadata, and comments via `comment_limit`) and `jira_download_attachments` (only when direct
  URL/local-file intake is unavailable). Don't re-run tool discovery once these are known to work.
- Extract text from document attachments before `clarify`, using the matching helper per type:
  - **PDF** → `python3 .agents/scripts/extract_jira_pdf_text.py <pdf> -o <out.txt>`
  - **DOCX** (`.docx`) → `python3 .agents/scripts/extract_jira_docx_text.py <docx> -o <out.txt>`
  Record the extraction status per attachment. Both exit `3` when no readable text is produced — then
  mark `OCR/manual inspection required` (PDF) or `manual inspection required` (DOCX) and do not treat
  that attachment as analyzed.

## Single development log comment

Keep **one** comment as the source of truth, marked `agent-development-log:v1` inside a `{noformat}`
block. Use the template at `.agents/adapters/templates/jira-development-log.jira`.

- Locate the active log via `jira_get_issue(comment_limit=...)` and the marker. If none exists, create one.
- **Only the active comment counts.** Ignore deleted, historical, or changelog-only bodies as decision
  sources — they prove history existed, not that a decision is current.
- Update the same comment after plan, implementation, tests, review, PR, CI, and QA handoff. No
  progress-comment spam.
- For `delivery: dual-branch`, fill the **Delivery** block: releasable + integration branch names, the
  integration merge/conflict status, the **Integration PR** link, the **Releasable PR** link (in order),
  and tick the matching Work Done rows. Log this as the steps happen. The PR links are the
  `links.self[0].href` returned by the Bitbucket REST API (`.agents/adapters/bitbucket.md`). Also record
  the **Jenkins `lastBuild` status** (`#N SUCCESS/FAILURE` + Jenkins URL + fix-attempt count) and, on
  failure, the **failure class + resume stage + console link** (`.agents/adapters/jenkins.md`) between the
  Integration and Releasable PR rows.
- If MCP comment write tools aren't exposed, use REST fallback: `POST /rest/api/2/issue/{key}/comment`
  to create, `PUT /rest/api/2/issue/{key}/comment/{id}` to update. Format with Jira wiki markup
  (`h2.`/`h3.`, tables, lists). Use explicit `{color:green}done{color}`/`pending` states, not `x` marks.

## Branch naming (when used with the bitbucket adapter)

Derive `BRANCH_NAME = ${JIRA_KEY}-${sanitized_summary}`: lowercase, transliterate Turkish chars to
ASCII, non-alphanumerics → `-`, collapse/trim `-`.
