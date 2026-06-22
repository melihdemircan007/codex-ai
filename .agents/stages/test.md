# Stage: Test

**Role:** adopt `.agents/roles/tester.md`.
**Driven by the profile's `tests` knob.** If `tests: []`, this stage is a **no-op** — state that
explicitly in the report and move on (some jobs/repos legitimately write no tests).

Test kinds map to the job's `areas`: `unit`/`api` belong to the **backend** area, `unit`/`component`
to the **frontend** area. For a full-stack job, write both sets against their respective slices.

## Per test kind

| Knob value | What to write |
|---|---|
| `unit` | Isolated tests for the changed units. Backend: JUnit 5 + Mockito + AssertJ, given/when/then — see `.agents/rules/testing-standards.md`. Use `.agents/skills/generate-tests.md` for templates. |
| `api` | Endpoint/contract tests for changed REST behavior (status codes, request/response shape, error paths). |
| `component` | Frontend component tests (Jasmine/Karma `*.spec.ts`) for changed UI behavior and states. |
| `integration` | Cross-component/service tests when behavior spans boundaries. Avoid requiring live external infra in unit runs. |

## Run them

- Maven module: `mvn test` (or `mvn clean verify` when integration/failsafe matters).
- Gradle module: `./gradlew test`.
- Frontend: `npm test` (and `npm run lint`).
- Run the **affected module(s)** only; full-workspace builds are not the default.

## Output

Test commands run + results (pass/fail with evidence). Failing tests block the `handoff` stage —
report them honestly rather than marking the stage done.
