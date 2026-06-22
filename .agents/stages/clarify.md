# Stage: Clarify (grill / decision gate)

**Goal:** Resolve every implementation-impacting ambiguity *before* planning, with a visible,
auditable decision ledger. This is the strongest gate in the workflow — a relentless but practical
grill that **explores the code to answer questions instead of guessing**, asks **one question at a
time** with a recommended answer, and walks the design branch by branch.
*(Technique inspired by mattpocock's grill-me / grill-with-docs.)*

## Depth (`clarify_depth` knob)

| `clarify_depth` | Behavior |
|---|---|
| `deep` | Full grill: walk the design tree branch by branch; surface **every** implementation-impacting decision **for explicit approval**; sharpen terminology; record ADRs for hard-to-reverse choices. (default) |
| `light` | Surface only the few **blocking** decisions; skip the exhaustive tree-walk — but still **confirm each with the user** (no silent close). (e.g. hotfix) |
| `none` | No grill — the profile omits `clarify` from `stages` entirely (e.g. library-bump). |

## Rules

- Always run as a **visible checkpoint** after `intake` and before `plan` (unless `clarify_depth: none`). Never skip it silently.
- A decision counts as "previously made" only if it is in the **active development log** (see the
  enabled tracker adapter) or the **current chat session**. Ignore deleted/historical/changelog snapshots.
- If prior decisions exist, list them and ask whether to reuse them before marking them reused.
- Anything that changes behavior, API contract, permissions, persistence, navigation, rollout,
  ownership, or QA expectations is **implementation-impacting** unless the requirement or an existing
  repo pattern already fixes it unambiguously.
- Never ask what you can answer by reading the repo, configs, tests, or CI files. Use
  `.agents/skills/endpoint-discovery.md` for code-level conventions.

## Decision ledger

Build **All Decisions Ledger** — every implementation-impacting decision you found, numbered, with its
**concrete value**, source/evidence, a recommended answer, and a status. **Evidence never closes a
decision by itself — it only supplies the recommended answer. Nothing is final until the user approves it.**

- `recommended (awaiting approval)` — your proposed answer (from evidence or judgment). **Not final.**
  Every decision starts here, including ones that look obvious from the repo/requirement.
- `open question` — genuinely ambiguous or conflicts with evidence (no confident recommendation).
- `user-confirmed` / `user-edited` — the user explicitly approved or changed it (record the exact evidence).
- `superseded by Dx` — a later decision overrode this one. **Keep the row visible (struck through), never
  delete it**, and never let plan/implement reintroduce it. See `.agents/rules/requirement-traceability.md`.

Give each decision a **stable id** (`D1`, `D2`, …) — this is the Decision Checklist carried through
plan → implement → review → handoff.

## Must-Not-Exist (negative requirements)

Maintain a separate **Must-Not-Exist** list for everything that must NOT be built, must be removed, or
must not change (e.g. "no *Temizle*/Clear button", "don't modify endpoint X"). Negative requirements are
the easiest to lose — they get their own list and are verified by **asserting absence** in `review`.
See `.agents/rules/requirement-traceability.md`.

For user-visible values (routes, menu labels, API paths, permission keys, feature names), show the
**concrete value** in the ledger — never hide it behind "repo pattern applies", and never silently
close it as proven.

## Terminology sharpening (deep)

When a term is **vague or overloaded** (classic: "Customer" vs "User", "order" vs "basket", "active"),
don't let it slide:
- Ask a clarifying question and propose a **canonical term** to use consistently.
- Cross-reference an existing glossary / `CONTEXT.md` / domain model if the repo has one; align with it.
- Record the resolved term in the ledger so the plan and code use one word for one concept.

## Hard-to-reverse decisions → ADR (deep)

Most decisions live only in the ledger. But when a decision is **genuinely hard to reverse** — public
API contract, persistence schema/migration, public naming, rollout/feature-flag strategy — capture it
as a short ADR at `.agents/decisions/ADR-<n>-<slug>.md` using `.agents/decisions/_TEMPLATE.md`. Keep it
lightweight; link it from the ledger. Do **not** create ADRs for easily-reversible choices.

## Asking — confirm EVERY decision (not just the open ones)

Surface the **whole ledger** to the user and get explicit approval for **every** item. Evidence-backed
decisions are presented for approval too — they are not skipped just because the repo "proves" them.

1. **Show the full numbered ledger** first — each row with its concrete value, evidence, and your
   recommended answer.
2. **`open question` items** → ask **one at a time**, each with a recommended answer. Never bulk-ask
   open questions. Record the answer before asking the next.
3. **`recommended (awaiting approval)` items** (evidence-backed / confident) → present them as a
   **numbered confirm-list** and ask the user to **approve all as shown, or name the ones to change**.
   The user may instead ask you to walk them **one at a time**, and may edit any item. Until the user
   responds, they stay `awaiting approval` — **do not** mark them confirmed yourself.
4. Record each result as `user-confirmed` or `user-edited` with the exact approval evidence.

A recommendation is only a recommendation. Evidence justifies the recommendation; it does **not**
substitute for the user's approval.

## Exit

- Do **not** move to `plan` until **every** ledger item is `user-confirmed` or `user-edited` — not just
  the open questions. No item may remain `awaiting approval` or `open question`.
- Never offer to start `implement` from here. After clarify you go to `plan`; implementation is only
  reachable after the separate `after_plan` gate.
- This stage is an `approval_gates: after_clarify` point — present the final approved ledger and wait
  for the user's explicit "go" before continuing.
