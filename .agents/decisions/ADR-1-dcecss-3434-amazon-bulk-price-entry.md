# ADR-1: DCECSS-3434 Amazon bulk price entry

- **Status:** accepted
- **Date:** 2026-06-19
- **Job / issue:** DCECSS-3434
- **Areas:** both

## Context

DCECSS-3434 provides a PDF analysis document for "Amazon Toplu Fiyat Girisi". The document targets
Backend & Frontend teams, defines an Ecom Admin catalog screen, and requires listing, filtering,
Excel template download, filtered export, and bulk Excel upload for Amazon fixed prices stored on
`PRODUCT_SALES_INFOS`.

The repository already separates admin UI/API concerns from catalog persistence:
`ecom-admin-client` owns the Admin screen, `ecom-admin-backend` owns admin-facing endpoints and
catalog-service proxying, and `product-catalog-service` owns `ProductSalesInfo` persistence.

## Decision

Implement DCECSS-3434 as a full-stack feature:

- `ecom-admin-client`: add the Ecom Admin catalog screen and menu entry.
- `ecom-admin-backend`: expose admin-facing endpoints for list/filter, template download, export,
  and upload.
- `product-catalog-service`: add the catalog persistence/query/update operations for Amazon fixed
  prices on existing `ProductSalesInfo` rows.

The backend API contract follows existing admin patterns rather than embedding the PDF's `/api`
prefix in application code:

- `POST amazon-prices/filter`
- `GET amazon-prices/export`
- `POST amazon-prices/upload`

Frontend implementation must follow `ecom-admin-client/AGENTS.md`; no `.spec.ts` or frontend test
files will be created even though the full-stack profile normally includes component tests.

The PDF's "Sablon Indir" feature is intentionally out of scope after clarification. The screen has
only `Excel Indir` and `Excel Yukle` Excel actions.

## Reversibility

This is hard to reverse because it establishes a new admin screen, menu/permission names, frontend
constants, backend endpoint paths, Excel format, and persistence behavior that QA and users will
exercise together.

## Consequences

The feature can be planned as backend contract first, then frontend consumption. Backend unit/API
tests remain in scope. Frontend verification is build/lint/manual behavior only because local
frontend guidance explicitly forbids test file creation.

## Alternatives considered

- Backend-only implementation: rejected because the Jira PDF defines a new Ecom Admin screen and UX.
- Direct frontend-to-catalog-service calls: rejected because existing admin patterns route UI calls
  through `ecom-admin-backend`.
