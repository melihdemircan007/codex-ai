# Adapter: Jenkins (CI)

**Optional.** Active only when a profile lists `jenkins` in `adapters`. If not listed, skip CI
monitoring; the user runs CI themselves.

## When to check

After the PR is approved/opened, or when the user asks. Do not rerun CI or merge without explicit
approval.

## Wait for the integration PR build (gate before the releasable PR)

For `delivery: dual-branch`, after the **integration PR** is opened the workflow **waits for its build
to finish** and gates the releasable PR on a green result. The status **and** the failure detail are read
**directly from Jenkins** — not the Bitbucket build-status API, and never the in-app browser.

### Jenkins env preflight (separate from git/Bitbucket creds)

Require — without printing — `JENKINS_URL`, `JENKINS_USER`, `JENKINS_PASSWORD`, and `JENKINS_JOB_PREFIX`
(the multibranch folder path, org-specific, e.g. `job/101671_E-COMMERCE/job/Microservices`). Any missing
→ **HALT and ask** the user to `export` them (or `source .env.local`). Auth is **HTTP Basic**:
`curl -u "$JENKINS_USER:$JENKINS_PASSWORD"`. These are Jenkins-only; git transport + Bitbucket REST still
use git's own credential.

### Locate the PR build and poll `lastBuild`

```bash
JOB="$JENKINS_URL/$JENKINS_JOB_PREFIX/job/$SLUG/job/PR-$PR_ID"
curl --http1.1 -sS -L --connect-timeout 10 --max-time 30 \
  -u "$JENKINS_USER:$JENKINS_PASSWORD" -H "Accept: application/json" \
  -w '\nHTTP_STATUS=%{http_code}\n' -o /tmp/jenkins-gate.json \
  "$JOB/lastBuild/api/json?tree=number,result,building"
# building:true → wait (re-poll ~30s); result SUCCESS → green; FAILURE|UNSTABLE|ABORTED → red; null → not started yet
# HTTP_STATUS != 200 → report and retry (Jenkins may be slow / auth wrong)
```

`lastBuild` is inherently the **newest run** — no stale-entry problem. Report progress; if not terminal
past a sensible timeout (~30 min), **ask the user** rather than spinning forever.

- **SUCCESS** → proceed to open the **releasable PR**.
- **FAILURE/UNSTABLE/ABORTED** → **HALT** and **diagnose from Jenkins** (next section), then run the fix
  loop from the mapped resume stage (R13): fix → re-merge releasable→integration → re-push → re-build →
  re-poll. **Repeat at most `ci_fix_attempts` (default 2)**; still red after the cap → **STOP and hand the
  diagnosis to the user**. **Never open the releasable PR until Jenkins `lastBuild` is SUCCESS.**

### Diagnose the failure (Jenkins API) — *why* it broke + *which stage to resume*

With the failed build number `N` (`$JOB/$N` or `$JOB/lastBuild`). **All Jenkins curls must include
`--http1.1 -L --connect-timeout 10 --max-time 60`** — Jenkins on-prem may reject HTTP/2 and curl hangs
without a timeout. Save output to file and capture `HTTP_STATUS`:

```bash
# 1) console log — save to file (can be large), grep for the error
curl --http1.1 -sS -L --connect-timeout 10 --max-time 60 \
  -u "$JENKINS_USER:$JENKINS_PASSWORD" \
  -w '\nHTTP_STATUS=%{http_code}\n' -o /tmp/jenkins-console.txt \
  "$JOB/$N/consoleText"

# 2) test report (JSON) — if test failures
curl --http1.1 -sS -L --connect-timeout 10 --max-time 30 \
  -u "$JENKINS_USER:$JENKINS_PASSWORD" -H "Accept: application/json" \
  -w '\nHTTP_STATUS=%{http_code}\n' -o /tmp/jenkins-tests.json \
  "$JOB/$N/testReport/api/json"

# 3) pipeline stages — which stage failed
curl --http1.1 -sS -L --connect-timeout 10 --max-time 30 \
  -u "$JENKINS_USER:$JENKINS_PASSWORD" -H "Accept: application/json" \
  -w '\nHTTP_STATUS=%{http_code}\n' -o /tmp/jenkins-stages.json \
  "$JOB/$N/wfapi/describe"
```

**If `consoleText` returns non-200 or times out**, fall back to classifying from the `api/json` result
field + the `testReport` (both are smaller and more likely to respond). Report the HTTP status so the
user knows the console was unreachable, don't silently say "failure details unavailable."

Extract the concrete root cause (error line / failing test / quality gate / failed stage), then
**classify and pick the resume stage**:

| Failure class | Signal in console/report | Resume stage |
|---|---|---|
| compile | javac/Kotlin/TS compile errors | `implement` → `test` |
| test (unit/integration/api) | `testReport` failures | `implement` (fix) → `test` |
| dependency | unresolved artifact / version conflict / lib not published | `implement` (+ build the lib first, `.agents/skills/multi-repo-feature.md`); if a dependency *decision* was wrong → back to `clarify`/`plan` |
| Sonar | quality gate / coverage threshold | `implement` (add tests / fix smells) → `review` |
| Fortify | security scan findings | `implement` + `review` (security lens) |
| packaging | jar/war/image build or artifact push | `implement` / config |
| deploy / infra / flaky / timeout | OpenShift/K8s/agent/network | **no code change** → re-trigger the build (within the cap); persistent infra → **escalate to the user** |

**Log to the Jira Delivery block:** failure class, failed stage/test, the Jenkins console link, the
**resume stage taken**, and the attempt count — using the latest run, never a stale success.

## Secrets

`JENKINS_URL` / `JENKINS_USER` / `JENKINS_PASSWORD` / `JENKINS_JOB_PREFIX` come from the environment
(kept in `.env.local`, gitignored). Never print or commit `JENKINS_PASSWORD`; if it leaks, recommend
rotation. Use runtime/CI-managed secrets only.
