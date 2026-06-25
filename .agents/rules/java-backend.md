# Rule: Java Backend Conventions

Applies to the Spring Boot services and BFFs (Java 17/Maven and Java 21/Gradle). Generalized from the
PSJ patterns; a service-local `.cursor/rules/*.mdc` or nested `AGENTS.md` may override for its module.

## Layering & request flow

```
HTTP Request → Filter → Controller → (Business) Service → Caller / CacheHandler / Repository → Mapper → Response
```

- Controllers extend the repo's base controller, delegate to services, return the standard response
  wrapper (e.g. `ResponseEntity<ApiResponse<T>>`).
- Services return the standard `ServiceResponse<T>` (or the module's equivalent).
- BFFs call downstream services through caller/wrapper layers — **never** call external REST directly.
- Don't add JPA/DB layers to a BFF that has none.

## Critical rules

1. **Constructor injection only** (`@RequiredArgsConstructor`); never `@Autowired` field injection.
2. Services return the standard response wrapper; don't leak raw downstream types.
3. Extend the base controller for new controllers.
4. Response/resource models `implements Serializable` with an explicit `serialVersionUID` (cache compat).
5. Use **Lombok** (`@Data`/`@Getter`/`@Setter`/`@Builder`/`@Slf4j`) — no hand-written boilerplate.
6. Use **MapStruct** for object mapping (interface, `componentModel = "spring"`).
7. Configuration via `@Value("${property}")` with sane env-var defaults — no hardcoded URLs/ports/topics.
8. Bean names get a module prefix to avoid clashes with shared libraries.
9. Logging via `@Slf4j` — never `System.out`/`System.err`.
10. Java 21 modules: prefer `getFirst()`/`getLast()`, `toLowerCase(Locale.ROOT)`.

## Build & test

- Maven: `mvn test` (`mvn clean verify` for integration). Gradle: `./gradlew test` then `./gradlew build`.
- **Local repository:** Maven builds use the developer's **shared local repo `~/.m2`** (the default).
  The workflow never passes `-Dmaven.repo.local` or `-s`, so every build — **including those inside git
  worktrees** — resolves from and caches into the one shared `~/.m2/repository` (no per-worktree `.m2`,
  no re-download). Don't hardcode an absolute `.m2` path; `~/.m2` is correct for every machine.
- Build the **affected module** before handoff; full-workspace build is not the default.
- Shared-lib changes: build the lib (publishes to mavenLocal) before its consumers.
