# Skill: Local Rules Discovery

How to reliably find and load **the guidance that belongs to whatever repo/module you're about to
edit**. Used by the `load-context` stage and as a precondition in `implement`.

## Why

Repo-local guidance in this monorepo is not in one place — it follows several conventions, and some
repos have none. Missing it leads to wrong patterns (e.g. ignoring `ecom-admin-client`'s screen
template). Always scan before editing.

## Scan order (most specific first)

For each target module directory `{module}`:

1. **`{module}/.cursor/rules/*.mdc`** — architecture/pattern rules (controller/service/mapper/testing/
   project-architecture, etc.). Present in ~4 PSJ services (e.g. `psj-catalog-search-bff`,
   `psj-content-bff`, `psj-cms-service`) and `ecom-ai-service`.
2. **`{module}/.cursor/skills/*/SKILL.md`** — module-scoped skills (e.g. `scaffold-cms-feature`,
   `scaffold-landing-page`, `generate-tests`, `psj-dev`). Present in ~8 modules.
3. **`{module}/AGENTS.md`** — module-level agent rules. Present in ~8 modules, **including the frontend
   `ecom-admin-client`** (which has no `.cursor/`).
4. **`{module}/CLAUDE.md`** — codebase docs (e.g. `customer-service`, `psj-cms-service`, `psj-content-bff`).
5. **`{module}/docs/*.md`** — convention docs and templates. Notably `ecom-admin-client/docs/`:
   `yeni-ekran-sablonu.md` (golden-standard new-screen template → `src/app/catalog/review/`),
   `filtre-alani-kurallari.md` (filter-field rules). Also check root `README.md` / `CONTRIBUTING.md`.
6. **Fallback:** if none exist, use the root `.agents/rules/` + `.agents/skills/` defaults.

## Quick discovery commands

```bash
M=<module>
ls "$M"/.cursor/rules/*.mdc 2>/dev/null
ls "$M"/.cursor/skills/*/SKILL.md 2>/dev/null
ls "$M"/AGENTS.md "$M"/CLAUDE.md 2>/dev/null
ls "$M"/docs/*.md "$M"/README.md "$M"/CONTRIBUTING.md 2>/dev/null
```

## Precedence

Local (closest) guidance **overrides** the root `.agents/` defaults on conflict — consistent with the
AGENTS.md nesting rule ("the file closest to the edited file wins"). Note explicit overrides so the user
sees them.

## Read, don't just list

Actually open and read the discovered files. Many carry **immutable** constraints (e.g.
`ecom-admin-client/AGENTS.md`: Angular 6, no tests, no new design patterns) and **copy-from-here**
templates. Treat them as binding for that module.
