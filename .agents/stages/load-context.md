# Stage: Load Context (repo-local guidance)

**Runs right after `intake`, before `clarify`/`plan`/`implement`.** Mandatory in every profile.

**Goal:** before reasoning or writing any code in a repo, **discover and read that repo's own
guidance** — its local rules, skills, conventions, and templates. A repo's local guidance is more
specific than the root defaults and **takes precedence on conflict (closest file wins).**

This stage exists because skipping it caused real misses (e.g. starting work in `ecom-admin-client`
without reading its `AGENTS.md` + `docs/` screen template).

## Steps

1. **Resolve the target module(s)/repo(s)** from `intake` (per the job's `areas`). For a full-stack job
   there may be more than one (e.g. `ecom-admin-backend` + `ecom-admin-client`) — do this for each.
2. **Discover local guidance** for each target using `.agents/skills/local-rules-discovery.md` (scan
   order below). **Read** what you find — don't just note it exists.
3. **Summarize the binding rules** you must follow for this module (immutable constraints, golden-standard
   examples, naming/structure conventions, "do NOT" lists, templates to copy).
4. **Resolve precedence:** where local guidance conflicts with a root `.agents/rules/*` or `.agents/skills/*`,
   **the local one wins** for that module. Note any such overrides explicitly.

## Scan order (per target module)

1. `{module}/.cursor/rules/*.mdc`
2. `{module}/.cursor/skills/*/SKILL.md`
3. `{module}/AGENTS.md`
4. `{module}/CLAUDE.md`
5. `{module}/docs/*.md` (+ root `README.md` / `CONTRIBUTING.md` when they carry conventions)
6. **Fallback:** if the module has none of the above, use the root `.agents/rules/` + `.agents/skills/` defaults.

## Output (report, no approval needed)

```
### Context loaded — <module>
- Loaded: <list of files actually read>  (or: "no local guidance — using root .agents/ defaults")
- Binding local rules: <2–5 bullets of the must-follow constraints / templates>
- Overrides root: <any local rule that supersedes a root rule, or "none">
```

Feed this into `clarify`, `plan`, and `implement`. Do not proceed to `implement` for a module whose
local guidance has not been loaded.
