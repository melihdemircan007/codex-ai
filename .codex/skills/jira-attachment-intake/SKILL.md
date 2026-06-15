---
name: jira-attachment-intake
description: Extract Jira issue attachment requirements, especially PDF analysis documents. Use when Jira intake finds PDF attachments, when MCP attachment output is embedded/base64 instead of a local file, or when Codex must turn Jira PDF attachments into readable text before Grill-Me Gate or technical planning.
---

# Jira Attachment Intake

## Workflow

Use this skill during Jira Intake whenever `jira_get_issue` reports PDF attachments.

1. Read Jira issue metadata with `jira_get_issue` first.
2. If any attachment has `content_type` `application/pdf` or a `.pdf` filename and metadata includes an attachment URL, prefer `scripts/jira_pdf_intake.py --attachment-url ...` so the PDF is downloaded directly to `/tmp` and no base64 blob is emitted into the chat/tool transcript.
3. Use Jira credentials only from environment variables (`JIRA_PERSONAL_TOKEN`, `JIRA_BASE_URL`) or Codex-owned MCP config passed via `--codex-config`. Never print token values, headers, or config contents.
4. Use `jira_download_attachments` only as a fallback when direct URL download is unavailable and no local PDF exists. The MCP tool can return a large embedded/base64 resource, which is expensive in context.
5. If MCP returns embedded/base64 resource content, save that MCP output as JSON when possible and parse it with `scripts/jira_pdf_intake.py`; do not paste or reprint the blob.
6. Use the generated `.txt` files as first-class requirements evidence before entering Grill-Me Gate.
7. If the script reports `no_text`, state that OCR or manual visual inspection is needed before treating the PDF as fully analyzed.

## Script Usage

Run from the repository root:

```bash
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320
```

Useful options:

```bash
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 --out /tmp/codex-jira-attachments
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 --attachment-url "https://jira.example.com/secure/attachment/123/analysis.pdf"
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 --attachment-url "/secure/attachment/123/analysis.pdf" --jira-url "https://jira.example.com"
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 --attachment-url "https://jira.example.com/secure/attachment/123/analysis.pdf" --codex-config ~/.codex/config.toml
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 --base64-stdin < /tmp/mcp-pdf-resource.json
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 --mcp-json /tmp/jira-download-attachments-output.json
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 --base64-file /tmp/pdf-blob.txt
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 --file /path/to/local.pdf
```

The script writes:

- PDFs downloaded from Jira attachment URLs, decoded from MCP embedded/base64 resources, or copied from local files under `/tmp/codex-jira-attachments/<ISSUE>/`
- Extracted text next to each PDF as `.txt`
- A JSON summary to stdout with file paths, page count, and status

## Direct Jira Attachment Download

Prefer this path when Jira metadata includes an attachment URL:

```bash
python3 .codex/skills/jira-attachment-intake/scripts/jira_pdf_intake.py DCECSS-3320 \
  --attachment-url "https://jira.example.com/secure/attachment/123/analysis.pdf"
```

Credential resolution order:

- Token: `JIRA_PERSONAL_TOKEN`, then `--token-env`, then `--codex-config` Atlassian MCP headers.
- Jira URL for relative attachment URLs: `--jira-url`, then `JIRA_BASE_URL`, then `--codex-config` Atlassian MCP headers.

The script must not print the token. If the network is sandbox-restricted, rerun the same helper command with escalated permissions instead of falling back to `jira_download_attachments`.

## Embedded MCP Attachment Input

When the Jira MCP attachment tool returns content like:

```json
[
  {
    "type": "resource",
    "resource": {
      "uri": "attachment:///DCECSS-3320/analysis.pdf",
      "mimeType": "application/pdf",
      "blob": "JVBERi0x..."
    }
  }
]
```

save that MCP output as JSON or pass it through stdin, then run the script with `--mcp-json` or `--base64-stdin`. The script will decode the PDF, write it under `/tmp/codex-jira-attachments/<ISSUE>/`, and extract text without needing Jira credentials or network access.

## Credentials

This skill may read Jira credentials only from environment variables or Codex-owned MCP config explicitly passed to the helper. It must not read Cursor/IDE configs, write tokens to files, or print tokens in command output. The MCP embedded/base64 path remains a fallback for cases where direct download is unavailable.
