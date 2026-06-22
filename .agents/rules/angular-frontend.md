# Rule: Angular Frontend Conventions

Applies to the Angular apps (`ecom-admin-client`, `seller-admin-client`, and other Node/Angular
clients). A project-local config may override for its app.

## Structure & patterns

- Feature modules under `src/app/**`; shared services/constants under `src/app/shared/**`.
- API endpoint strings live in the central constants file (e.g.
  `ecom-admin-client/src/app/shared/service/constants.ts`) — add new endpoints there, don't inline URLs.
- Routes go in the feature's `*.routing.ts`. Menu/sidebar/permission placement in
  `sidebar.component.ts`. Use `.agents/skills/endpoint-discovery.md` to find the right files.
- Reuse existing components and styles before adding new ones; match the existing module's structure.

## Conventions

- Follow the app's established state-management and HTTP-service patterns (don't introduce a new one).
- Keep components focused; move shared logic into services.
- Externalize user-facing strings for i18n where the app already does so.
- No hardcoded environment values — use the app's `environment.*.ts` / config.

## Build & test

- `npm install` (or `ci`), `npm run build`, `npm test` (Jasmine/Karma), `npm run lint`.
- Component behavior is covered by `*.spec.ts` tests (the `component` test kind).
