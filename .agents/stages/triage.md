# Stage: Triage  (orchestrator entry — Step 1)

**This is the first thing the orchestrator does, before any profile is selected.** It is *not* listed in
any profile's `stages:` — the profile doesn't exist yet at this point. Keep it lightweight; the heavy
requirement work happens later in the full `intake` stage.

**Goal:** take in the incoming job, classify it, and recommend a profile + `areas` — then stop for approval.

## Steps

1. **Read the job lightly.** Use the user's request as-is. If an issue key is present and a tracker is
   reachable, skim only the summary/title (do *not* download attachments or run full intake yet).
2. **Classify the area(s):**
   - `backend` — Java/Spring services, BFFs, APIs, libs, persistence, server logic.
   - `frontend` — Angular apps, UI, components, routes, styling.
   - **both** — the job needs server *and* UI changes (e.g. a new admin feature = API in
     `ecom-admin-backend` + screen in `ecom-admin-client`).
3. **Detect signals:** was a **design** provided (Figma link / screenshots)? Is there an **issue key**?
4. **Recommend a profile + areas** (see the table in `.agents/workflow.md` Step 1):
   - backend only → `backend-feature`, `areas:[backend]`
   - frontend only → `frontend-feature`, `areas:[frontend]`
   - both → `fullstack-feature`, `areas:[backend, frontend]`
   - version bump → `library-bump`; urgent fix → `hotfix` (set `areas` to what the fix touches)

## Output — recommendation + STOP

Present a one-paragraph recommendation with rationale and the detected signals, then **STOP and wait
for the user's approval** (`after_triage`, always on):

```
### Triage — awaiting approval
- Job: <one line>
- Areas detected: backend / frontend / both  (why)
- Design provided: yes/no   · Issue key: <key or none>
- Recommended profile: <profile>  ·  areas: [...]
Approve this profile, or tell me to use a different one?
```

Do not begin `intake` until the user approves (they may correct the profile/areas).
