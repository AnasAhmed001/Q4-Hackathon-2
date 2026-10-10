---
id: 014
title: Frontend 500s Root Cause And Deploy Script Defects
stage: green
date: 2026-10-10
surface: agent
model: deepseek-v4-flash
feature: local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: /sp.implement
labels: ["kubernetes", "helm", "minikube", "nextjs", "bugfix", "deployment", "phase-4"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - frontend/app/(protected)/chat/actions.ts
 - frontend/app/(protected)/tasks/actions.ts
 - frontend/app/api/chat/history/route.ts
 - frontend/app/api/chat/send/route.ts
 - charts/todo-chatbot/values.yaml
 - charts/todo-chatbot/templates/configmap.yaml
 - deploy/deploy.sh
 - specs/004-local-kubernetes-deployment/research.md
tests:
 - "docker run --entrypoint sh todo-chatbot-frontend:dev -c \"grep -rq 'localhost:30080' .next/static && echo BAKED_OK\" (T034 gate) — PASS"
 - "docker run --entrypoint sh todo-chatbot-frontend:dev -c 'grep -c BACKEND_URL .next/server' — runtime read now present, was 0"
 - "curl -s -o /dev/null -w '%{http_code}' http://localhost:30080/login — 200"
 - "curl http://localhost:30800/health — 200"
 - "curl http://localhost:30800/api/docs — 200"
 - "POST http://localhost:30080/api/chat/send — 400 (was 500)"
 - "POST http://localhost:30080/api/chat/history — 405 (GET-only route, was 500)"
 - "kubectl logs deploy/todo-chatbot-frontend | grep -c ECONNREFUSED — 0"
 - "bash -n deploy/deploy.sh — syntax OK"
---

## Prompt

### Prompt 1 (owner bug report, with two DevTools screenshots)

```text
so the sign in works but the the task fetching api is giving 500 error and also
the chatbot is giving 500 error i have checked the database and it is up and running
```

Screenshots showed `POST http://localhost:30080/tasks` → 500 and
`POST http://localhost:30080/api/chat/send` → 500.

### Prompt 2 (AskUserQuestion answer — scope of the source fix)

I reported that the fix required a **third** frontend source change beyond the two this phase
authorized (T024, T025), and offered three options. The owner chose:

```text
Reorder the 4 call sites (Recommended)
```

### Prompt 3 (tool-call rejection, then)

```text
i just started docker dekstop u have to check if the containers are running
```

### Prompt 4

```text
resume where we left
```

## Response snapshot

**Root cause of both 500s was one line, repeated in four server files.**

```ts
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';
```

`NEXT_PUBLIC_*` is inlined by `next build`, so the first operand is a **string literal**, the `||`
short-circuits, and Terser **constant-folds the whole expression** — `process.env.BACKEND_URL` was
not shadowed, it was **deleted from the bundle**. Every server-side call therefore went to the
browser-facing `http://localhost:30800`, which inside the pod is the pod's own loopback →
`ECONNREFUSED` → 500. This is the D6 trap one level down.

Sign-in masked it because Better Auth's DB path reads `DATABASE_URL`, a genuine **runtime** variable
from `secretKeyRef` — so half the app worked and suspicion fell on the database.

The decisive evidence was in the **adjacent line of the same files**, already correct and already
working:

```ts
const AUTH_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000';
```

Runtime-first. So the fix was to make the `BACKEND_URL` line consistent with its own neighbour, not
to redesign anything (spec.md:265 — existing Phase III sources are the starting point).

**Fix applied** — reordered all four server call sites; added `config.backendUrl` to `values.yaml`
and `BACKEND_URL` to the ConfigMap. `frontend/lib/api-client.ts` deliberately untouched — that is the
browser path, which genuinely needs the host-published port.

Verified after rebuild: server bundle now reads
`process.env.BACKEND_URL || "http://localhost:30800"`, `.next/static` still carries
`localhost:30800` (T034 gate still passes), `POST /api/chat/send` → 400, `POST /api/chat/history` →
405, zero `ECONNREFUSED`.

**Two further defects surfaced while proving the fix landed**, both on the **update** path
(FR-012 / SC-009) and both invisible on a clean install:

1. **`minikube image load` silently no-ops when the node already holds that tag.** Prints nothing,
   exits 0, keeps the old image. Measured: node `dev` still `sha256:71500a13…` (8 days old) after the
   script printed "✓ loaded both images"; a collision-free tag `t2` imported fine as
   `sha256:a5830cbdfddf…`. The pod was running **new ConfigMap values with old code** — which
   excludes a config fault and points at the image.
2. **`helm upgrade` does not roll pods.** Same image tag string → byte-identical pod template → no
   new ReplicaSet; and helm never restarts pods for a changed ConfigMap. REVISION 4 reported
   `deployed` while pods stayed `AGE 8d`, one ReplicaSet per Deployment dated 8 days earlier.

Both fixed in `deploy/deploy.sh` (step 5 drops the stale tag before loading; step 7 runs
`kubectl rollout restart deploy` + `rollout status`), with the observed evidence in comments.
`bash -n` → OK.

Also recorded (not a deliverable defect, but the trap a reader will hit): `helm upgrade --set`
**persists** in user-supplied values across later upgrades — needed `--reset-values` to return the
release to the chart's declared state.

Findings written up as **research.md §5.10–§5.12**, and §5.9's count corrected from eight to eleven.

## Outcome

- ✅ Impact: The reported 500s are resolved at the source and verified in-cluster. Three defects that
  made a "successful" deployment ship the wrong code are closed, two of them permanently in
  `deploy.sh`. FR-012/SC-009's update path — previously broken while looking correct — now delivers
  what it declares.
- 🧪 Tests: All nine checks in `tests:` above pass. Browser-level verification (T036–T037) still
  requires the owner.
- 📁 Files: 4 frontend server files (identical one-line reorder), `values.yaml`, `configmap.yaml`,
  `deploy/deploy.sh`, `research.md`.
- 🔁 Next prompts: Owner runs T036 (sign-in + one full conversational task operation in the browser)
  and T037 (`/tasks/<id>/edit` client-side call must target `localhost:30800`). Then T038–T056,
  T064, T065, T067.
- 🧠 Reflection: The most useful artifact in this whole diagnosis was a **neighbouring line of code
  that already did the right thing**. Three separate "correct in the cluster, absent in the process"
  symptoms all reduced to the same shape: a mechanism behaving exactly as documented, against an
  expectation that was never checked. `minikube image load` and `helm upgrade` are not buggy — the
  procedure assumed delivery semantics they do not provide. And none of it was visible while every
  automated gate passed green.

## Evaluation notes (flywheel)

- Failure modes observed:
  - **Trusting a command's success message over its effect.** `✓ loaded both images` and helm's
    `deployed` were both true statements about the command and false statements about the system.
    Grepping the built bundle was what finally distinguished them.
  - **Assuming a passing gate means the artifact is current.** T034/step 4 passed throughout,
    because it checks the *browser* URL — which was never the broken one. A gate that tests the wrong
    half of a two-half contract reads as green while the other half fails.
  - **Suspecting configuration before measurement.** The instinct was to add `BACKEND_URL` to the
    ConfigMap; only grepping `.next/server` for the identifier showed there was no runtime lookup to
    influence. One grep would have saved a rebuild cycle.
  - **Tooling error on my side:** monitoring grep anchored `^==>` while `say()` emits ANSI codes
    first — the pattern never matched and looked like silence from the build.
- Graders run and results (PASS/FAIL): `bash -n deploy/deploy.sh` PASS. T034 bundle gate PASS.
  In-cluster HTTP probes PASS. End-to-end `deploy.sh` re-run over an existing cluster — **NOT YET
  EXERCISED**; the step 5 and step 7 fixes are syntax-checked and reasoned but not replayed. That
  belongs to T065.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Re-run `deploy.sh` end-to-end against the **existing**
  cluster (the update path, not a clean one) and confirm the node's image ID changes without the
  manual `docker rmi` — that single measurement validates both step 5 and step 7 at once.
