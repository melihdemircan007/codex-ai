# Adapter: Bitbucket (pull requests)

**Optional.** Active only when a profile lists `bitbucket` in `adapters`. If not listed, the
`handoff` stage produces a PR description as plain text for the user to use manually.

## Git remote auth preflight (mandatory before any network git op)

The workflow uses the **user's ambient git credentials** (SSH key or the OS credential helper) — it does
**not** inject any token. Before any `git fetch`, `git worktree add origin/<base>`, push, or PR, just
**verify** that ambient auth works — never blindly fetch.

- Cheap check, per affected module M: `git -C "$ROOT/M" ls-remote origin -h >/dev/null 2>&1`.
  Exit 0 → auth works, proceed.

### On auth failure: HALT, WAIT, then take username/password to continue

If `ls-remote` is non-zero, the run **stops mid-flow and waits** — never proceed, never silently fall
through. Report the failure and offer two ways forward:

- **(a) Set up SSH / OS credential helper** (no creds entered into the workflow):
  - **SSH** (typical for Bitbucket): add an SSH key to Bitbucket; remote uses `git@<host>:…`
    (`git -C "$ROOT/M" remote -v`); test `ssh -T git@<host>`.
  - **OS credential helper:** macOS `git config --global credential.helper osxkeychain`, then do one
    manual `git -C "$ROOT/M" fetch` so git stores the credential.
- **(b) Provide a git username + password now** so the run can continue. Recommend pasting a Bitbucket
  **HTTP access token as the password** (with your username), not a real account password. Hold them
  only in the **in-memory credential cache for this session** — never the repo, never the remote URL:
  ```bash
  HOST=$(git -C "$ROOT/M" remote get-url origin | sed -E 's#https?://([^/]+)/.*#\1#')
  git config --global credential.helper 'cache --timeout=3600'
  printf 'protocol=https\nhost=%s\nusername=%s\npassword=%s\n\n' "$HOST" "$USER" "$PASS" | git credential approve
  ```
  Then **re-run the `ls-remote` preflight**; on success continue (fetch/push/PR reuse the cache).
- **Security:** never print the password, never write it to a repo file or the remote URL; it lives only
  in the in-memory cache and expires with the timeout. If it leaks, recommend rotation.
- **Offline fallback** (if auth can't be set up at all now): proceed from **existing local refs** (a
  local base branch or current `HEAD`) with an explicit "base may be stale" warning, or switch the run to
  `isolation: in-place`. **Do not push or open a PR** until auth is fixed.

Never resume any stage while the auth check is failing — wait for credentials (or fixed ambient auth)
and a passing preflight.

## Branch preparation (before implementation, local only)

For each repo where code will be written:
- **Run the git remote auth preflight above first.** Only fetch once `ls-remote` succeeds (or the user
  chose the offline/in-place fallback).
- `git fetch`, then verify the base refs exist (this repo uses `origin/releasable` and
  `origin/integration`; adjust per repo if different).
- **If `isolation: worktree`** (default): create a **git worktree** per affected repo off the base
  branch — follow `.agents/skills/worktree-isolation.md`. All work happens in the worktree; the main
  working tree is untouched and worktrees are **kept** (not removed). The PR is opened from the
  worktree's branch.
- **If `isolation: in-place`**: create local branches from the remote bases in the main tree, e.g.:
  - `feature/${BRANCH_NAME}-releasable` from `origin/releasable`
  - `feature/${BRANCH_NAME}-integration` from `origin/integration`
- If a branch already exists, inspect and reuse only if it's the intended work; otherwise ask.
- **Local only:** do not commit, push, open PRs, or merge during preparation.

## Delivery model: dual-branch (when `delivery: dual-branch`)

The change must land on **both** the integration line and the releasable line, via **two PRs**. With
`isolation: worktree` there are two worktrees per repo (`…-releasable`, `…-integration`). Sequence:

1. **Author + finish + test** in the **releasable** worktree (`feature/<BRANCH>-releasable`). When the
   code is done, work on that branch is complete.
2. **Port releasable → integration:** in the integration worktree, merge the releasable feature branch:
   ```bash
   git -C "$ROOT/.worktrees/<JIRA>/M-integration" merge "feature/<BRANCH>-releasable"
   ```
   **Resolve any conflicts**, then build/test the integration worktree.
3. **Auth preflight, then push both** branches (`feature/<BRANCH>-integration`, `feature/<BRANCH>-releasable`).
4. **Open PR #1 → integration** (`feature/<BRANCH>-integration` → `origin/integration`).
5. **Wait for the integration build to go green** before the next PR — `.agents/adapters/jenkins.md`
   (poll **Jenkins** `lastBuild` via `JENKINS_*`; red → diagnose from Jenkins + fix loop capped at
   `ci_fix_attempts` from the mapped resume stage, else HALT).
6. **Open PR #2 → releasable** (`feature/<BRANCH>-releasable` → `origin/releasable`) — only once the
   integration build is green.

- **Integration PR is opened first**, then the releasable PR.
- Each push and each PR is a **separate outward-facing action**: STOP for explicit approval **before the
  integration PR** and again **before the releasable PR** (`before_pr` triggers once per PR).
- The PR-readiness checklist below applies to **both** PRs.
- **Log every step to the Jira dev log** (`.agents/adapters/jira.md` Delivery block): both branch names,
  integration merge/conflict status, Integration PR link, Releasable PR link, in order.
- For `delivery: single-branch`, this collapses to one branch and one PR.

## PR-readiness checklist (verify before opening)

- [ ] Acceptance criteria mapped to implementation and tests.
- [ ] Clarify decisions captured in the development log (if `jira` enabled).
- [ ] Scope limited to the requested behavior.
- [ ] Tests added/updated for changed behavior (per the `tests` knob) and passing locally.
- [ ] Affected module build passed locally, or the blocker is documented.
- [ ] Review found no unresolved critical/high issues.
- [ ] PR description has issue key, summary, changed areas, test commands+results, risks, QA notes.
- [ ] No secrets/tokens committed.

## Opening the PR — via Bitbucket REST API (no browser, no env vars)

PRs are created **headlessly through the Bitbucket Server REST API**. **Do not attempt, wait on, or even
mention the in-app browser — go straight to REST.** There are **no `BITBUCKET_*` env vars**: everything
is derived from the git remote, and auth reuses **git's own credential** (the same one git uses for
commit/push). Prepare the description, **ask for explicit approval**, then POST.

### Derive everything from the remote + git credential

```bash
REMOTE=$(git -C "$M" remote get-url origin)              # https://USER@stash.turkcell.com.tr/git/scm/ec101671/<repo>.git
NOCRED=$(printf '%s' "$REMOTE" | sed -E 's#://[^@/]+@#://#')         # strip user@
HOST=$(printf '%s' "$NOCRED" | sed -E 's#https?://([^/]+)/.*#\1#')   # stash.turkcell.com.tr
BASE=${NOCRED%%/scm/*}                                   # https://stash.turkcell.com.tr/git
REST=${NOCRED#*/scm/}                                    # ec101671/<repo>.git
PROJECT=$(printf '%s' "$REST" | cut -d/ -f1 | tr '[:lower:]' '[:upper:]')   # EC101671 (REST key is UPPERCASE)
SLUG=$(printf '%s' "$REST" | cut -d/ -f2 | sed 's/\.git$//')

# auth = git's stored credential for this host (keychain / credential helper — same as push):
CRED=$(printf 'protocol=https\nhost=%s\npath=git\n\n' "$HOST" | git -C "$M" credential fill)
GUSER=$(printf '%s' "$CRED" | sed -n 's/^username=//p')
GPASS=$(printf '%s' "$CRED" | sed -n 's/^password=//p')
```

### Create the PR

```bash
curl -sS -X POST -u "$GUSER:$GPASS" -H "Content-Type: application/json" \
  -w 'HTTP_STATUS=%{http_code}\n' -o /tmp/pr.json \
  "$BASE/rest/api/1.0/projects/$PROJECT/repos/$SLUG/pull-requests" \
  -d '{"title":"<KEY> <summary>","description":"…",
       "fromRef":{"id":"refs/heads/feature/<BRANCH>-integration"},
       "toRef":{"id":"refs/heads/integration"}}'
```

- **HTTP 401/403** → git has no usable credential for the host → **HALT** and run the credential-setup
  flow (collect git username/password → `git credential approve`, see the git-auth preflight above) so
  **git itself** holds the creds, then retry. **Never ask for `BITBUCKET_*` env vars.**
- **2xx** → capture the PR URL (`.links.self[0].href`) and log it to the Jira Delivery block.
- The build gate (`.agents/adapters/jenkins.md`) reads the source commit from the PR detail:
  `GET $BASE/rest/api/1.0/projects/$PROJECT/repos/$SLUG/pull-requests/$PR_ID` → `.fromRef.latestCommit`.
- **Dual-branch (R10):** open PR #1 `…-integration → integration` first, then PR #2
  `…-releasable → releasable` — each its own approval.
- **Cloud fallback** (if ever on Bitbucket Cloud): `POST {base}/2.0/repositories/{workspace}/{repo}/pullrequests`.
- **Security:** credentials come from git's store only — never printed, never in a repo file, URL, or chat.

Pushing/opening/merging are each separate outward-facing actions — confirm each one.
