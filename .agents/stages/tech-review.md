# Stage: Tech Review (developer comment)

**Runs between `clarify` and `plan`, only when the profile sets `dev_review: true`.** If `dev_review:
false`, this stage self-skips (state it briefly and move on).

**Why here:** by now the agent has read the Jira/requirement, loaded repo-local guidance, inspected the
code, and grilled the decisions — but has **not yet locked a plan**. This is the point where a senior
**developer's technical opinion** can still reshape the approach cheaply, or send the work back for a
fresh look, before any implementation decision is set.

This is distinct from `clarify`: clarify is the agent asking the user to resolve ambiguities;
tech-review is the **developer volunteering technical steering** ("do it via service X", "the analysis
missed Y", "watch the Z pattern").

**Role:** present as the relevant analyst(s) per `areas` (`backend-analyst` / `frontend-analyst`).

## Steps

1. **Post a concise technical reading** (not the full plan yet):
   - the approach you intend to take, in 3–6 bullets;
   - key alternatives you considered and why you leaned one way;
   - risks / sharp edges / things you're unsure about;
   - reuse opportunities (existing services, components, patterns) you found in the code;
   - anything in the analysis you suspect is incomplete or off.
2. **Ask explicitly for the developer's comment** — free-form. Make clear it's optional: an empty/"looks
   good" response means proceed.
3. **Act on the comment:**
   - minor steer → adjust the approach and note it;
   - "the analysis is wrong / missing X" → **loop back** to `clarify` (or `intake`) and re-examine with
     that lens, then return here;
   - new constraint/decision → add it to the **Decision Checklist**; if it reverses an earlier decision,
     mark that one `superseded` (`.agents/rules/requirement-traceability.md`).
4. **Record** the developer comment and how it was resolved in the dev log (Developer Notes / Tech Review).

## Exit

This stage pauses for the developer comment (`after_tech_review`). Proceed to `plan` only after the
comment is received (or the developer says proceed) and any resulting checklist changes are reflected.
Do not silently skip the request when `dev_review: true`.
