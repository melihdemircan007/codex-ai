# Rule: Requirement Traceability

Cross-cutting policy that keeps every confirmed requirement tied to the code — so nothing decided gets
dropped, **especially negative requirements** ("won't exist / will be removed / don't touch X"). Born
from a real miss: a reversed decision ("no *Clear* button") wasn't carried into implementation.

Referenced by `clarify`, `plan`, `implement`, `review`, and `handoff`. This file is the single home of
the policy; the stages just hook into it.

## 1. One Decision Checklist

- `clarify` produces **one** Decision Checklist: every confirmed decision as a row with a **stable id**
  (`D1`, `D2`, …), the concrete value, and its status (`user-confirmed` / `user-edited` / `superseded`).
- This checklist is the single source of truth carried through plan → implement → review → handoff. Do
  not keep parallel/divergent copies. If a tracker adapter is on, it lives in the dev log.

## 2. Superseded decisions (never silently drop)

- When a later user decision overrides an earlier one, mark the **old** row `superseded by Dx`
  explicitly (keep it visible — strike it through, don't delete). The new row is the active one.
- A `superseded` decision must **not** be reintroduced by plan/implement. If one reappears in code,
  that's a traceability failure.

## 3. Must-Not-Exist list (negative requirements)

- Maintain a separate **Must-Not-Exist** list for every negative requirement: things that must NOT be
  built, must be removed, or must not change (e.g. "no *Clear* button", "do not modify endpoint X",
  "remove legacy toggle Y").
- Negative requirements are the easiest to lose because there's no artifact to point at — they need
  their own explicit list and their own verification (assert **absence**).

## 4. Re-verify before implementation

- The `after_plan` gate report must include the **final Decision Checklist + Must-Not-Exist list** so
  the user confirms them one last time before any code is written.

## 5. Verify each item in review

- `review` runs a **traceability pass**: for every checklist item, point to the code that satisfies it;
  for every Must-Not item, confirm it is **absent**. Confirm no `superseded` item was reintroduced.

## 6. Done means fully traced

- **Do not mark the job done** (no handoff/PR-ready) if a single item is unmet, contradicted, missing
  its code evidence, or if a Must-Not item exists / a superseded item reappeared. List the gap instead.

## Checklist shape (example)

```
Decision Checklist
- D1  Endpoint path = /v1/amazon-price            [user-confirmed]   → code: AmazonPriceController
- D2  Add "Temizle" (Clear) button                [superseded by D3]
- D3  No "Temizle" (Clear) button                 [user-confirmed]
Must-Not-Exist
- N1  No "Temizle"/Clear button on the screen     → review: confirmed absent
- N2  Do not change existing /v1/price endpoint   → review: confirmed unchanged
```
