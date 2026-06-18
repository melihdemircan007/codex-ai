---
name: ecommerce-endpoint-discovery
description: Token-efficient endpoint discovery for the ECommerce repo. Use when Codex needs to find or design ECommerce admin/catalog endpoints, frontend Constants URLs, Angular routes, sidebar/menu entries, permissions, or Spring controller mappings without broad rg output.
---

# ECommerce Endpoint Discovery

Use this skill before repo exploration for endpoint, menu, route, or permission work in this repository.

## Core Rule

Start from canonical files and narrow candidates. Do not begin with repo-wide regex searches that combine controller annotations, frontend constants, menu terms, and permissions.

Avoid first-pass commands like:

```bash
rg -n "@RequestMapping|@GetMapping|@PostMapping|@PutMapping|@DeleteMapping" ecom-admin-backend/src/main/java -S
rg -n "Constants|sidebar|permission|role|menu|Menu|AUTH|authority" ecom-admin-client/src ecom-admin-backend/src/main -S
```

## Discovery Flow

1. Normalize the domain terms from the task or Jira, for example `amazon price`, `amazon-price`, `product-sales-info`, `commission`.
2. Find candidate files with filenames-only output:

```bash
rg -l "amazon-price|amazonPrice|product-sales-info|productSalesInfo" ecom-admin-client/src/app ecom-admin-backend/src/main/java product-catalog-service/src/main/java --glob '!**/target/**'
```

3. Read only the best candidate files or small line ranges with `sed -n`.
4. Summarize the found evidence before running another search.
5. Broaden only when the canonical sources do not answer the question.

## Canonical Sources

- Frontend endpoint strings: `ecom-admin-client/src/app/shared/service/constants.ts`
- Frontend service call pattern: the relevant component under `ecom-admin-client/src/app/**`
- Angular routes: the relevant `*.routing.ts` file, usually under the feature module
- Sidebar and menu placement: `ecom-admin-client/src/app/sidebar/sidebar.component.ts`
- Admin backend external endpoints: relevant controller files under `ecom-admin-backend/src/main/java/com/turkcell/ecommerce/admin/controller/**`
- Admin-to-service proxy/accessor paths: relevant accessor/service classes under `ecom-admin-backend/src/main/java/com/turkcell/ecommerce/admin/**`
- Product catalog internal endpoints: relevant controller/service/repository files under `product-catalog-service/src/main/java/com/turkcell/ecommerce/catalog/**`

## Output Limits

- Prefer `rg -l` over `rg -n` during candidate discovery.
- If `rg -n` is necessary, constrain both path and term set, and use `--max-count`.
- Keep command output small enough to inspect directly; read additional chunks only after identifying why they are needed.
- For file reads, use narrow `sed -n` ranges instead of full files unless the file is short.

## Endpoint Decision Checklist

When proposing an endpoint, report:

- frontend constant/path evidence;
- admin controller path evidence;
- internal service/catalog path evidence, when applicable;
- whether the path follows nearby naming conventions;
- any mismatch between Jira/PDF wording and existing repo conventions.
