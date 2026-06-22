# Skill: Endpoint Discovery

Token-efficient discovery for endpoint, route, menu, permission, or Spring controller-mapping work.
Use it before broad repo exploration (called from `intake`, `clarify`, and the backend-analyst role).

## Core rule

Start from **canonical files** and narrow candidates. Do **not** start with repo-wide regex that mixes
controller annotations, frontend constants, menu terms, and permissions.

Avoid first-pass commands like:
```bash
rg -n "@RequestMapping|@GetMapping|@PostMapping" <backend>/src/main/java -S
rg -n "Constants|sidebar|permission|menu|authority" <frontend>/src <backend>/src/main -S
```

## Flow

1. Normalize the domain terms (e.g. `amazon price`, `amazon-price`, `product-sales-info`).
2. Find candidates with **filenames only**:
   ```bash
   rg -l "amazon-price|amazonPrice|product-sales-info" <frontend>/src/app <backend>/src/main/java --glob '!**/target/**'
   ```
3. Read only the best candidates or small line ranges.
4. Summarize evidence before searching again.
5. Broaden only when canonical sources don't answer the question.

## Canonical sources (this repo)

- Frontend endpoint strings: `ecom-admin-client/src/app/shared/service/constants.ts`
- Angular routes: the relevant feature `*.routing.ts`
- Sidebar/menu/permission placement: `ecom-admin-client/src/app/sidebar/sidebar.component.ts`
- Admin backend external endpoints: controllers under `ecom-admin-backend/src/main/java/com/turkcell/ecommerce/admin/controller/**`
- Admin proxy/accessor paths: services/accessors under `ecom-admin-backend/src/main/java/com/turkcell/ecommerce/admin/**`
- Catalog internal endpoints/persistence: `product-catalog-service/src/main/java/com/turkcell/ecommerce/catalog/**`
- PSJ BFFs: controllers under `psj-*-bff/src/main/java/.../controller/**`

## Output

When proposing an endpoint, report: frontend constant/path evidence, controller path evidence,
internal service path evidence (if any), whether it follows nearby naming, and any
requirement-vs-repo naming mismatch.
