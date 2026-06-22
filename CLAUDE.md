@AGENTS.md

# Claude-specific notes

The shared, tool-agnostic instructions live in `AGENTS.md` (imported above). Everything there
applies to Claude Code too. The notes below are Claude-only conveniences and do not change the workflow.

- Treat `.agents/skills/*.md` as skills: read the relevant one before doing endpoint discovery,
  test generation, multi-repo features, or code review.
- Use the TodoWrite/Task tools to track multi-stage jobs, but the **approval gates in
  `.agents/workflow.md` still govern** — stop and wait for the user at each gate regardless.
- When a profile enables the `jira` adapter and credentials are missing, stop and ask the user to
  set `JIRA_BASE_URL` / `JIRA_PERSONAL_TOKEN` before reading any issue data.
