# Stage: Intake

**Goal:** Understand the work before touching code. Produce a short *Requirement Digest*.

## Source of the requirement

- If `jira` is in the profile's `adapters`: follow `.agents/adapters/jira.md` to read the issue
  (summary, description, **all attachments**, acceptance criteria). Run the credential preflight first.
- If no issue-tracker adapter is enabled: take the requirement from the user's prompt and any
  files/links they provided. Ask for missing acceptance criteria rather than guessing.

## Attachments

Treat attachments as first-class requirement sources (PDF, DOCX, images, spreadsheets). Extract text
with the helper that matches the file type, before continuing:
- **PDF** → `python3 .agents/scripts/extract_jira_pdf_text.py <pdf> -o <out.txt>`
- **DOCX** → `python3 .agents/scripts/extract_jira_docx_text.py <docx> -o <out.txt>`

If a helper produces no readable text (exit `3`), record `OCR/manual inspection required` (PDF) /
`manual inspection required` (DOCX) and do not treat that attachment as analyzed.

## Detect design input (when `design_input: auto`)

If the profile's `design_input` is `auto`, note whether the task/prompt/attachments include a **design
artifact** — a Figma link, exported frames, or screenshot images. Record `design present: yes/no`; this
is the signal the `design-analysis` stage reads to decide whether to run or self-skip. Do not ask for a
design if none was provided.

## Adopt the analyst role(s) for the job's areas

Per the profile's `areas`: for `backend` adopt `.agents/roles/backend-analyst.md` (+ `java-backend.md`
rules); for `frontend` adopt `.agents/roles/frontend-analyst.md` (+ `angular-frontend.md` rules); for
both, cover both. This shapes what you look for in intake and how you frame decisions.

## Identify scope

- Affected service(s)/module(s), expected behavior, scope boundaries, likely test impact.
- When `areas` has both backend and frontend, note the cross-area contract (which API the UI consumes).
- For endpoint/route/menu/permission/controller-mapping questions, use
  `.agents/skills/endpoint-discovery.md` (narrow, canonical-source search — no broad repo-wide greps).

## Output — Requirement Digest

Produce before leaving this stage:
- Requirement source (issue key or prompt) + attachment list with extraction status.
- **Concrete target module(s)/repo(s)** the work will touch (e.g. `ecom-admin-backend`,
  `ecom-admin-client`) — the next stage `load-context` reads these to find each repo's local guidance.
- Acceptance criteria summary.
- Evidence-backed implementation decisions.
- Unresolved ambiguities or repo/requirement mismatches (these feed `clarify`).

> Reading the requirement does not need approval. Do **not** start planning or coding here.
