# Skill: Generate Tests

Templates and a gap-finding strategy for writing missing unit tests. Used by the `test` stage and
the tester role. Generalized from the PSJ patterns; adapt names to the target module.

## Step 1 — Find gaps

Scan for production files without a matching test:
```bash
find <module>/src/main -name "*Service.java" | while read f; do
  test=$(echo "$f" | sed 's|src/main|src/test|; s|\.java|Test.java|')
  [ ! -f "$test" ] && echo "MISSING: $test"
done
```
Repeat for `*Mapper.java`, `*Operation.java`, `*Controller.java`, `*DynamicComponentService.java`.

## Step 2 — Apply a template

**Service test** (extend the module's base test class where one exists, e.g. `BaseUnitTest`):
```java
class XServiceTest extends BaseUnitTest {
    @InjectMocks private XService service;
    @Mock private XDependency dependency;

    @Test
    void method_returnsSuccess_whenDependencySucceeds() {
        // given
        when(dependency.call(any())).thenReturn(new ServiceResponse<>(data));
        // when
        var response = service.method(input);
        // then
        assertThat(response.isSuccess()).isTrue();
        verify(dependency).call(any());
    }

    @Test
    void method_returnsFail_whenDependencyFails() { /* failure path */ }
}
```

**Mapper test** — use `Mappers.getMapper(XMapper.class)`; cover null input, empty collection,
all-fields-mapped, null-field handling.

**Controller test** — `@ExtendWith(MockitoExtension.class)`; verify HTTP status, service delegation,
response wrapping.

**Thin delegate service** (e.g. component services) — test `getType()` returns the right enum, that
`getContent()` delegates, and the failure path.

## Conventions

- Naming: `methodName_expectedOutcome_whenCondition` (preferred) or `shouldX_whenY`.
- given/when/then in every test; AssertJ `assertThat`.
- Prefer `@ParameterizedTest` (`@ValueSource`/`@CsvSource`/`@MethodSource`, `provideXxx` providers)
  over duplicated methods.
- Load JSON fixtures from `src/test/resources/` via the shared `objectMapper`.
- No `@SpringBootTest` for unit tests; no live Redis/Kafka/DB; don't test private methods directly.

## Step 3 — Verify

Run `./gradlew test` (or `mvn test`) and confirm compilation + all tests pass.
