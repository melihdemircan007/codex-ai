# Adapter: Jenkins (CI)

**Optional.** Active only when a profile lists `jenkins` in `adapters`. If not listed, skip CI
monitoring; the user runs CI themselves.

## When to check

After the PR is approved/opened, or when the user asks. Do not rerun CI or merge without explicit
approval.

## Classify failures

Read the build result and classify the failure so the fix path is obvious:

| Class | Typical signal |
|---|---|
| compile | javac/Kotlin/TS compile errors |
| test | unit/integration test failures |
| dependency | unresolved artifact, version conflict, lib not published |
| Sonar | quality gate / coverage threshold failed |
| Fortify | security scan findings |
| packaging | jar/war/image build or artifact push failed |
| deploy | OpenShift/K8s deploy or health-check failed |

Identify the shortest safe fix path. Record the build link, status, and classification in the
development log (if `jira` enabled). For a dependency failure on a shared lib, check whether the lib
needs to be built/published before the consumer (see `.agents/skills/multi-repo-feature.md`).

## Secrets

Never print CI tokens or credentials. Use runtime/CI-managed secrets only.
