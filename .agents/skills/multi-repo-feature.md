# Skill: Multi-Repo Feature

Coordinate a feature that spans several modules. Used from `plan` and `implement` when a change
touches shared libs + consumers. Key rule: **build libraries before their consumers.**

## Step 1 — Impact

Determine affected modules and order. Representative chains in this repo (PSJ stack):

| Feature type | Modules, in order |
|---|---|
| New CMS data type | `psj-cms-service` → BFFs (`psj-content-bff` / `psj-catalog-search-bff`) |
| New CMS data type (searchable) | `psj-cms-service` → BFFs → `psj-elastic-command-service` → `psj-elastic-query-service` |
| New product feature | `psj-product-bff-lib` → BFFs |
| New shared functionality | `psj-common-bff-lib` → `psj-product-bff-lib` → BFFs |
| ES index field | `psj-elastic-command-service` → `psj-elastic-query-service` |

## Step 2 — Dependency order

```
psj-common-bff-lib   (shared base)
  → psj-product-bff-lib   (product enrichment)
    → psj-content-bff / psj-catalog-search-bff   (deployable BFFs)
psj-cms-service        (CMS types propagate to BFFs)
psj-elastic-command-service → psj-elastic-query-service
```

Libraries first — build/publish locally before consumers:
```bash
cd psj-common-bff-lib && ./gradlew build   # publishes to mavenLocal
```

## Step 3 — Branches & implementation

Create `feature/{ISSUE}-{desc}` in each affected repo (from its base branch). Implement lib changes
first, build, then wire consumers, then verify each with `./gradlew test`.

## Step 4 — Report per repo

Summarize files added per module and the build/test status of each.

## Common pitfalls

Library not published before consumer; wrong dependency order; enum/name mismatch across modules;
missing cache handler; snapshot version mismatch.
