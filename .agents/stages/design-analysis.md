# Stage: Design Analysis

**Design is optional.** Whether this stage runs depends on the profile's `design_input` knob:

| `design_input` | Behavior |
|---|---|
| `none` | Skipped entirely (backend jobs). |
| `auto` | Runs **only if** a design artifact was actually provided (detected at `intake`). If none, **skip** and record: *"No design provided — proceeding with requirement-only analysis."* |
| `figma` / `screenshots` | Always runs, using that source (a design is expected/required). |

So a frontend job with no Figma/screenshots simply skips this stage and continues like a backend job
(intake → clarify → plan → …). Do not block or ask for a design when `design_input: auto` and none exists.

**Role (when it runs):** adopt `.agents/roles/frontend-analyst.md`.

**Goal:** Turn visual design into concrete, buildable UI decisions before planning.

## Steps (only when a design is present)

1. Identify the design source:
   - `figma` (or `auto` + a Figma link) — read the Figma frames/links the user provided (use a Figma
     MCP/tool if available; otherwise ask the user to export the relevant frames or specs).
   - `screenshots` (or `auto` + attached images) — read the attached images.
2. Extract a **UI spec**: components and their states, layout/spacing, typography, colors,
   responsive breakpoints, interaction/animation, copy/i18n strings, and accessibility needs.
3. Map each design element to the existing component library and conventions
   (see `.agents/rules/angular-frontend.md`). Reuse existing components before proposing new ones.
4. Flag mismatches between the design and what the codebase/back-end can currently support — these
   become `open question` items for the `clarify` stage.

## Output

- If a design was present: a short UI spec — component list (reuse vs. new), states, design tokens,
  responsive rules, and any design-to-code gaps. Feeds `clarify` and `plan`.
- If skipped: a one-line note that no design was provided and the job continues on requirements alone.
