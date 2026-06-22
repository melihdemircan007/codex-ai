# Stage: Plan

**Goal:** Structure the work into execution slices by *behavior/deliverable*, not by file.

## Steps

1. Break the work into internal **execution slices** (e.g. Backend API, Proxy/Accessor, Frontend UI,
   Validation, Permissions/Config, Tests, Review, Handoff) — only those that fit the job.
   - **Slice per area.** When `areas` has both backend and frontend, produce backend slice(s) and
     frontend slice(s), and **order the backend contract slice first** so the UI builds against a
     settled API. Use `.agents/skills/multi-repo-feature.md` for dependency ordering (one branch per
     repo, one dev log, one coordinated PR cycle).
2. For each slice capture: changed behavior, files/modules likely affected, tests to add (per the
   profile's `tests` knob), risks, and which acceptance criteria it covers.
3. **Map every Decision Checklist item to a slice** (by id `D1`, `D2`, …), and carry the
   **Must-Not-Exist** list forward — nothing from `clarify` may be dropped. Don't plan anything
   `superseded`. See `.agents/rules/requirement-traceability.md`.
4. Link every plan assumption back to a **confirmed decision** from `clarify` or to repo/requirement
   evidence. If a new implementation choice appears, return to `clarify` — do not invent it here.
4. Prefer the **smallest change** that satisfies the acceptance criteria.
5. If a tracker adapter is enabled, write the plan into the development log (see `.agents/adapters/jira.md`);
   default to one issue + one log, no physical sub-tasks unless multi-team/multi-PR/risky rollout. For
   `delivery: dual-branch`, record **both** branch names per repo (`feature/<BRANCH>-releasable` and
   `feature/<BRANCH>-integration`).
6. For multi-repo features, follow `.agents/skills/multi-repo-feature.md` for dependency ordering
   (libraries built before consumers).

## Output

The execution-slice plan + test strategy, **plus the final Decision Checklist and Must-Not-Exist list**
restated for the user's last confirmation before any code is written. This is an `approval_gates:
after_plan` point — STOP and get explicit approval. Approval to implement is **not** approval to commit,
push, open a PR, rerun CI, or hand off.
