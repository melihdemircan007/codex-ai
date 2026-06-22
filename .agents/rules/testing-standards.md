# Rule: Testing Standards

Shared testing conventions. The `test` stage and tester role follow these; templates are in
`.agents/skills/generate-tests.md`.

## Backend (JUnit 5)

- **JUnit 5 + Mockito + AssertJ** (`assertThat` preferred).
- Extend the module's base unit-test class where one exists (e.g. `BaseUnitTest`, which provides
  `MockitoExtension` + a configured `ObjectMapper`). Controller tests may use
  `@ExtendWith(MockitoExtension.class)` directly.
- **given / when / then** structure in every test method.
- Naming: `methodName_expectedOutcome_whenCondition` (preferred) or `shouldX_whenY`.
- `@Mock` + `@InjectMocks`; build common data in `@BeforeEach`.
- MapStruct mappers: instantiate via `Mappers.getMapper(...)`.
- Load JSON fixtures from `src/test/resources/` via the shared `objectMapper`.
- **Prefer `@ParameterizedTest`** (`@ValueSource`/`@NullAndEmptySource`/`@EnumSource`/`@CsvSource`/
  `@MethodSource`) over duplicated `@Test` methods; `@MethodSource` providers are `static`, named `provideXxx`.

## What to test

| Layer | Verify |
|---|---|
| Controller | HTTP status, service called, response wrapping |
| Service | business logic, cache reads, null/edge cases, failure paths |
| Mapper | null input, collection mapping, field transforms |
| Util | edge cases, null inputs, boundaries |

## Do NOT

- No `@SpringBootTest` for unit tests; no live Redis/Kafka/DB — mock them.
- Don't test private methods directly; test through the public API.
- Don't skip given/when/then; don't forget `verify()` where interactions matter.
- Don't use lazy mocks (`thenReturn(null)` everywhere, empty objects, repeated `"test"` strings).

## Frontend

Jasmine + Karma `*.spec.ts`; cover component states (default/loading/empty/error) and interactions.

## Scope

Run the **affected module's** tests; a job with `tests: []` writes none (state it explicitly).
