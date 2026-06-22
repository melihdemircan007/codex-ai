# Stage: Review

**Role:** adopt `.agents/roles/reviewer.md`.
**Driven by `review_passes` (how many rounds) and `reviewers` (which lenses per round).**

This is what makes review depth vary by job: a hotfix may use `review_passes: 1, reviewers: [self]`,
while a risky backend change uses `review_passes: 2, reviewers: [self, security]`, and a critical one
could use 3–4 passes across more lenses.

## Each pass

Run one pass per `review_passes`. In each pass, apply every lens in `reviewers`:

| Lens | Focus |
|---|---|
| `self` | Bugs, regressions, missing tests, drift from acceptance criteria, unnecessary changes. |
| `security` | Secrets in code, injection, authz/permission gaps, unsafe deserialization, hardcoded URLs/credentials. |
| `architecture` | Pattern compliance (constructor injection, `ServiceResponse`, `BaseController`, layering) per `.agents/rules/`. |
| `performance` | N+1 calls, missing caching, needless allocations on hot paths. |

Use `.agents/skills/code-review.md` for the concrete checklist and scan commands.

## Traceability pass (always, in addition to the lenses)

Run a **requirement-traceability pass** every review (`.agents/rules/requirement-traceability.md`):
- For **each** Decision Checklist item (`D1`, `D2`, …), point to the code that satisfies it.
- For **each** Must-Not-Exist item, confirm it is **absent** (e.g. the *Clear* button does not exist).
- Confirm no `superseded` decision was reintroduced.
- A single unmet, contradicted, or unverifiable item — or any Must-Not item that exists — **blocks
  handoff**. List the gap; don't wave it through.

## Between passes

Fix valid findings before the next pass. Re-run the relevant tests after fixes. A later pass should
verify the earlier pass's fixes actually hold.

## Output

Findings grouped by severity (critical / warning / info) with `file:line` references, plus what was
fixed. No unresolved critical/high issues may remain before `handoff`.
