# Skill: Code Review

Concrete checklist + scan commands for the `review` stage. Apply the categories relevant to the
`reviewers` lenses in effect.

## Gather changes

```bash
git diff <base>...HEAD --name-only
git diff <base>...HEAD
```

## Category 1 — Pattern compliance (lens: architecture)

| Rule | Check | Fix |
|---|---|---|
| Constructor injection | no `@Autowired` field injection | `@RequiredArgsConstructor` |
| Service return type | services return `ServiceResponse<T>` | wrap result |
| Controller base | controllers extend `BaseController` | add it; pass `HttpServletRequest` to `super` |
| Serializable DTOs | response/resource models `implements Serializable` | add it + `serialVersionUID` |
| Lombok | no hand-written getters/setters/ctors | `@Data`/`@Builder`/`@Getter` |
| No direct REST | services go through caller/cache wrappers | route through wrapper |

## Category 2 — SonarQube smells (lens: self/architecture)

Unused imports (S1128), unused locals (S1481), dead stores (S1854), duplicated literals 3+ (S1192),
high cognitive complexity (S3776), possible NPE (S2259), lambda→method-ref (S1602), `System.out`
(S106 → use `@Slf4j`), utility class public ctor (S1118), swallowed `InterruptedException` (S2142).

## Category 3 — Java 21 conventions (lens: self)

`list.get(0)`→`getFirst()`, `get(size-1)`→`getLast()`, `toLowerCase()`→`toLowerCase(Locale.ROOT)`.

## Category 4 — Mock / hardcoded values in production (lens: self/security)

Production code (non-test) must not contain stubs or hardcoded env values:
```bash
rg "return null;" --type java --glob '!**/test/**' --glob '!*Test.java'
rg "// TODO|// FIXME|// HACK" --type java --glob '!**/test/**'
rg '"https?://[^"]+' --type java --glob '!**/test/**' --glob '!*application*.yml'
rg -i '"(password|secret|token|api.?key)"' --type java --glob '!**/test/**'
```
Move URLs/ports/topics/crons to `@Value("${...}")` / config; secrets to env/vault; magic numbers to
named constants; cache keys to enums.

## Category 5 — Security lens

Secrets in diff, injection (SQL/command/template), missing authz/permission checks, unsafe
deserialization, sensitive data in logs.

## Category 6 — Test coverage (lens: self)

Each new `*Service`/`*Mapper`/`*Controller`/`*Operation` has a matching `*Test`. List missing tests.

## Output

```markdown
## Review (pass N): <branch>
### Critical (must fix)
- [File:Line] issue — Fix: …
### Warnings (should fix)
- …
### Info (consider)
- …
### Test coverage
- New prod files: X · new test files: Y · missing: …
```
