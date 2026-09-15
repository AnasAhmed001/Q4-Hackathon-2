# Implementation Plan: Phase IV — Local Kubernetes Deployment of the Todo Chatbot

**Branch**: `004-local-kubernetes-deployment` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/004-local-kubernetes-deployment/spec.md`

**Status**: Draft — awaiting owner review. No code written yet.

---

## Summary

Re-host the existing Phase III Todo AI Chatbot (Next.js 16 frontend + FastAPI backend) as two
containerized workloads on a local Minikube cluster, installed and updated as **one Helm release**
called `todo-chatbot`.

The application source is **not** redesigned. This plan adds packaging (two container images, one
Helm chart) and a documented deployment procedure (build → load → install → verify). Four small
source-level changes are required, each forced by an explicit requirement rather than by preference
— see [Touch Points](#touch-points) and [Section K1](#k1-frontends-trustedorigins-is-hardcoded--required-source-change).

**Two findings changed the shape of this plan and are not anticipated by the spec:**

1. **The backend calls the frontend.** `backend-api/src/auth/jwt_validator.py:49-59` fetches the
   Better Auth JWKS endpoint at `BETTER_AUTH_URL + /api/auth/jwks`. In-cluster, that must be the
   frontend Service DNS name, *not* the browser-facing URL. The single variable `BETTER_AUTH_URL`
   therefore needs **two different values** depending on which pod consumes it. Resolved by using the
   dedicated `BETTER_AUTH_JWKS_URL` override (which takes priority at `jwt_validator.py:51`) for the
   backend, leaving `BETTER_AUTH_URL` unambiguous for the frontend.
2. **The frontend hardcodes its trusted origins** at `frontend/lib/auth-server.ts:51-55`
   (`http://localhost:3000`, a Vercel URL). FR-007 requires allowed origins to be deploy-time
   configuration and forbids embedding them in the repository. This must become env-driven, or
   browser sign-in silently fails at any port that isn't 3000.

---

## Approach

The pipeline is a single documented, idempotent sequence. Every step is a command, not a manual act.

```
 ┌─ 0. PREFLIGHT ─────────────────────────────────────────────────────────┐
 │  toolchain present · correct kubectl context · no colliding install    │
 │  pinned nodePorts free · host ports free · chart/build ports agree     │
 │  → any conflict: exit non-zero naming the conflicting value (FR-028)   │
 └────────────────────────────────────────────────────────────────────────┘
                                    │
 ┌─ 1. PROVISION DATA ────────────────────────────────────────────────────┐
 │  Neon: create branch `phase-iv` from existing project (copy-on-write)  │
 │  → schema arrives intact; no migration, no restructuring (FR-020)      │
 └────────────────────────────────────────────────────────────────────────┘
                                    │
 ┌─ 2. BUILD ─────────────────────────────────────────────────────────────┐
 │  docker build backend   (existing Dockerfile, python:3.12-slim)        │
 │  docker build frontend  (NEW multi-stage, output:'standalone')         │
 │    └─ NEXT_PUBLIC_* injected as --build-arg, values read from the      │
 │       chart's values.yaml so chart and bundle cannot drift             │
 │  Gordon (`docker ai`) assists; fallback to docker CLI, recorded        │
 └────────────────────────────────────────────────────────────────────────┘
                                    │
 ┌─ 3. LOAD INTO MINIKUBE ────────────────────────────────────────────────┐
 │  minikube image load <both images>   (docker driver has its own daemon)│
 │  → guarantees a clean-cluster run needs no undocumented transfer       │
 └────────────────────────────────────────────────────────────────────────┘
                                    │
 ┌─ 4. CONFIGURE SECRETS ─────────────────────────────────────────────────┐
 │  kubectl create secret generic ... --from-env-file=.env.deploy \       │
 │    --dry-run=client -o yaml | kubectl apply -f -                       │
 │  → idempotent, declarative-shaped, credential never committed          │
 └────────────────────────────────────────────────────────────────────────┘
                                    │
 ┌─ 5. INSTALL / UPGRADE ─────────────────────────────────────────────────┐
 │  helm upgrade --install todo-chatbot charts/todo-chatbot \             │
 │    -n todo-chatbot --create-namespace --wait                           │
 │  → one command installs fresh OR updates in place (FR-012)             │
 └────────────────────────────────────────────────────────────────────────┘
                                    │
 ┌─ 6. VERIFY ────────────────────────────────────────────────────────────┐
 │  kubectl get pods    → Running/Ready                                   │
 │  open http://localhost:30080 → sign in → chat → task appears           │
 └────────────────────────────────────────────────────────────────────────┘
```

**Why `helm upgrade --install` for both paths.** The spec requires re-running the procedure to be an
in-place update with zero duplicates (FR-012, SC-009). Rather than branching on "does a release
exist?", a single `helm upgrade --install` is inherently idempotent. Fresh install and upgrade are the
same command; only the preflight's collision detection distinguishes "this is my installation" from
"this is someone else's".

**Exposure: NodePort with pinned ports, reached at `localhost`.** Two Services, both type `NodePort`,
with `nodePort` declared in `values.yaml` (never cluster-assigned — FR-006). Host reachability comes
from the Minikube **docker driver's published-port mapping**:

```
minikube start --driver=docker --ports=30080:30080,30800:30800
```

This maps Windows `localhost:30080` → the Minikube node's `:30080`, where the NodePort listener
already is. The result is a **pinned, predictable `http://localhost` address with no hosts-file entry
and no extra long-running host process** — strictly better than the port-forward fallback the spec's
edge case anticipated. Documented fallback if `--ports` is unsupported by the driver in use:

```
kubectl port-forward --address 127.0.0.1 svc/todo-chatbot-frontend 30080:3000
kubectl port-forward --address 127.0.0.1 svc/todo-chatbot-backend  30800:7860
```

The fallback deliberately publishes the **same port numbers**, so the addresses baked into the
frontend image stay valid either way. That property is what makes the fallback safe to document
without changing the build.

---

## Key Decisions

### D1 — Docker image structure: per-service, and *different shapes by necessity*

| Service | Shape | Rationale |
|---|---|---|
| **Backend** | **Single-stage**, reuse existing `backend-api/Dockerfile` | Already exists, already correct: `python:3.12-slim`, deps installed in a cached layer before `COPY . .`, `CMD uvicorn src.main:app --host 0.0.0.0 --port 7860`. A single stage is honest here — there is no compile step whose toolchain should be excluded, and `python:3.12-slim` is already a minimal base. Adding a builder stage would add moving parts for no size or security win. |
| **Frontend** | **Multi-stage** (deps → builder → runner), new file | Not a preference — a requirement. Next.js `output: 'standalone'` exists precisely to emit a traced runtime tree; producing it needs a build stage with **devDependencies** (typescript, tailwind, eslint), which must not ship in the final image. A single stage would either ship ~500MB of build tooling or need hand-pruning. |

**Trade-off accepted:** the two services have structurally different Dockerfiles. This is a deliberate
asymmetry — uniformity here would mean either bloating the backend or hand-rolling the frontend.
Constitution III requires parity of *artifacts and declarative structure* between environments, not
between the two unlike services.

**Frontend runner-stage specifics** (verified against Next.js v16.1.1 docs):
- `next.config.ts` gains `output: 'standalone'`.
- Copy `public/`, `.next/standalone/`, `.next/static/` — `standalone` does **not** copy the last two
  automatically.
- `ENV PORT=3000`, and critically **`ENV HOSTNAME="0.0.0.0"`** — without it the standalone server
  binds to the container hostname and is unreachable from the pod network.
- `npm ci` must run with devDependencies present, so `NODE_ENV=production` is set **only after**
  dependency installation (build stage), never during it.
- `USER node` (non-root) — satisfies FR-017.

**Rejected:** building both from one shared Dockerfile with a `SERVICE` build-arg. It hides two
genuinely different lifecycles behind a conditional and makes the frontend's `--build-arg` env
injection awkward.

---

### D2 — Helm chart structure: one chart, two workloads

**Decision:** a single chart at `charts/todo-chatbot/` owning a ServiceAccount, a ConfigMap, a Secret
reference, two Deployments and two Services.

**Rationale:** the spec settles this for us — Assumption 1 (one installation owning both workloads),
FR-002 ("a single named installation, applied as one declarative unit"), and the acceptance criterion
that one `helm install` deploys both services. `helm upgrade --install` then gives atomic
install/upgrade and a single rollback unit.

**Trade-offs:**

| | One chart (chosen) | Separate charts |
|---|---|---|
| Install/upgrade atomicity | ✅ one release, one `--wait`, one rollback | ❌ two releases, ordering and partial-failure handling are manual |
| Matches spec's "one installation" | ✅ directly | ❌ requires a parent/umbrella chart to pretend to be one |
| Per-service independent versioning | ❌ both move together | ✅ |
| Reuse of a service elsewhere | ❌ must extract | ✅ |

The rejected column's advantages are real but belong to a later phase. Phase IV has one consumer and
one cluster; independent versioning of two services that are always deployed together is unused
capability. **Rejected alternative:** an umbrella chart plus two subcharts — strictly more files and
more Helm indirection for the same two Deployments, and it makes `--set` paths longer without adding
a single guarantee.

**Resources deliberately *not* in the chart:** no Ingress (NodePort is the decided mechanism), no HPA
(out of scope — autoscaling policies are explicitly deferred), no NetworkPolicy (hardening not
required by any FR; noted as a follow-up), no metrics stack (SC-010 forbids needing one).

---

### D3 — Pinned NodePorts: one source of truth, read by both sides

This is the highest-risk decision in the plan, because the frontend's browser-facing addresses are
**compile-time constants**. A mismatch between the chart's `nodePort` and the image's baked URL
produces a symptom that looks like an application bug (spec Risk #1).

**Decision:** `charts/todo-chatbot/values.yaml` is the **single source of truth**. The build script
*reads* the ports out of it rather than duplicating them, and a guard proves the two agree afterwards.

Declared values:

| Workload | Container port | `nodePort` | Host address |
|---|---|---|---|
| frontend | `3000` | **`30080`** | `http://localhost:30080` |
| backend | `7860` | **`30800`** | `http://localhost:30800` |

Build-time injection (ports parsed from `values.yaml`, no new tooling — plain `awk`):

```bash
FE_NP=$(awk '/^frontend:/{f=1} f&&/nodePort:/{print $2; exit}' charts/todo-chatbot/values.yaml)
BE_NP=$(awk '/^backend:/{f=1}  f&&/nodePort:/{print $2; exit}' charts/todo-chatbot/values.yaml)

docker build -f frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:${FE_NP}" \
  --build-arg NEXT_PUBLIC_BACKEND_URL="http://localhost:${BE_NP}" \
  -t todo-chatbot-frontend:${TAG} frontend/
```

**Three-layer consistency guarantee:**

1. **Single source** — the ports exist in exactly one file. The script cannot drift from the chart
   because it reads the chart.
2. **Preflight assertion** — before building, the script asserts both parsed values are non-empty and
   inside the valid NodePort range, and that the host ports are free. A parse failure aborts rather
   than silently baking `http://localhost:` into the bundle.
3. **Post-build proof** — after building, the script asserts the value actually landed in the bundle:

   ```bash
   docker run --rm --entrypoint sh todo-chatbot-frontend:${TAG} \
     -c "grep -rq 'localhost:${BE_NP}' .next/static && echo BAKED_OK"
   ```

   This is the check that catches a stale image when someone changes a port and forgets to rebuild.
   It is the concrete mitigation for spec Risk #1.

**Consequence to document loudly (spec edge case):** changing a declared port requires a **frontend
image rebuild**. The ConfigMap cannot correct it at runtime, because `NEXT_PUBLIC_*` values are
inlined into the browser bundle by `next build`. The quickstart states this in a warning block.

---

### D4 — Preflight collision detection

**Decision:** a `preflight` step runs to completion **before any mutating command**, performs seven
checks, and exits non-zero with a message that names the conflicting value (FR-028). Nothing is
partially applied because nothing is applied until every check passes.

| # | Check | Command | Refuses when |
|---|---|---|---|
| 1 | Cluster reachable and **correct context** | `kubectl config current-context` | context is not `minikube` — prevents deploying to a cloud context by accident |
| 2 | Toolchain present | `docker`, `minikube`, `helm`, `kubectl`, `docker ai` | any missing → prints the install command (FR-021/022 make installing them part of the procedure, so this is a *guide*, not a blocker) |
| 3 | **Release-name collision** | `helm list -A -o json` | a release named `todo-chatbot` exists in a **different** namespace, or a different release owns our namespace |
| 4 | **Namespace collision** | `kubectl get ns todo-chatbot -o jsonpath=...` + label check | the namespace exists and is not owned by our release (`app.kubernetes.io/instance != todo-chatbot`) |
| 5 | **Pinned nodePort in use** | `kubectl get svc -A -o json` → scan every `spec.ports[].nodePort` | `30080` or `30800` is claimed by a Service not owned by our release → names the port **and** the owning `namespace/service` |
| 6 | **Host port free** | bind test on `127.0.0.1:30080` / `:30800` | the host port is taken → names the port (needed for the docker-driver `--ports` mapping) |
| 7 | **Chart ↔ build port agreement** | parse `values.yaml`, compare to baked image label | mismatch → "port changed, rebuild required" |

**The upgrade path is not a collision.** Check 3 must distinguish:
- release `todo-chatbot` exists in namespace `todo-chatbot` → **our** installation → proceed to
  `helm upgrade` (FR-012).
- release `todo-chatbot` in namespace `staging`, or release `other-app` in namespace `todo-chatbot` →
  **collision** → refuse.

Ownership is determined by the standard Helm labels (`app.kubernetes.io/instance`), which Helm applies
to every resource it creates — so no custom bookkeeping is needed.

**Error contract** (one line, machine-greppable, names the value):

```
ERROR: nodePort-collision: 30080 already claimed by Service 'default/other-app' (release 'other-app')
```

**Rejected alternative:** letting the failure surface from `helm install`/the API server. It fails
*after* partial application in some cases, and the raw API error names neither the pinned value nor
the owning resource — which the spec explicitly forbids ("MUST NOT fail with an opaque low-level
error").

**Implementation note:** check 5 needs to read all Services cluster-wide. That is a read, runs on the
operator's machine against their own local cluster, and requires no cluster-side permissions — the
chart itself still grants the workloads **no** API access (see D7).

---

### D5 — Neon: a **branch**, wired through a gitignored env file into an immutable Secret

**Provisioning decision — branch, not a new database, not the Phase III database.**

Neon branches are copy-on-write clones of a parent branch. Creating `phase-iv` from the existing
project's default branch means the Better Auth tables *and* the task tables **already exist**, with
the identical schema and zero rows of Phase III production data.

This is the only option that satisfies FR-020 without work the spec forbids:
- Using Phase III's live branch → violates "repeatable and non-destructive" (SC-005 runs the suite
  twice; manual verification creates and deletes tasks).
- Creating an empty database → requires running Alembic migrations or the Better Auth schema SQL to
  recreate the schema, which is schema *restructuring* by another name, and needs `alembic/versions/`
  which is **gitignored** in this repo (`backend-api/.gitignore`). A branch sidesteps this entirely.

**Mechanism — ⚠️ SPEC IS SILENT (see [Open Questions](#open-questions--spec-silences) Q1).** `neonctl`
is **not installed** in this environment, and no Neon MCP server is available. Three candidates:

| Option | Trade-off |
|---|---|
| `neonctl branches create` (install CLI as a procedure step) | Automatable and repeatable, consistent with FR-021/022's "installing the toolchain is part of the procedure". Adds a tool. |
| Neon console (manual, once) | Zero new tooling; the branch is created once and its URL pasted into a gitignored file. Not scriptable. |
| Neon REST API via `curl` | No new tool *binary*, but needs an API key handled as a secret and hand-rolled JSON/PAT auth. |

**Recommendation:** console or `neonctl` for the *one-time* branch creation (a genuinely one-per-phase
act, not a per-deploy step), with the connection string then flowing through the repeatable path below.
The per-deploy path stays fully automated regardless of which is chosen. **This needs the owner's
call before `tasks.md`.**

**Wiring — the repeatable part:**

```
.env.deploy  (gitignored, lives beside the repo, never committed, never in an image)
   ├── DATABASE_URL=postgresql://...@ep-...-pooler.../neondb?sslmode=require
   ├── BETTER_AUTH_SECRET=...
   ├── COHERE_API_KEY=...
   └── ...
        │
        ▼
kubectl -n todo-chatbot create secret generic todo-chatbot-secrets \
  --from-env-file=.env.deploy \
  --dry-run=client -o yaml | kubectl apply -f -
        │
        ▼
Secret `todo-chatbot-secrets` ── secretKeyRef (optional:false) ──▶ both Deployments
```

Three properties this buys, each tied to a requirement:

- **Idempotent and declarative-shaped** (`--dry-run=client -o yaml | kubectl apply -f -`) — satisfies
  constitution I, where a bare `kubectl create secret` would raise "is this a manual mutation?"
  questions. Re-running is a no-op update, not a duplicate.
- **Never committed, never baked** — the value lives only in a gitignored file and in the cluster's
  Secret. The chart's `templates/secret.yaml` is **not** used to carry credentials; the chart
  references an existing Secret by name (`existingSecret`), so no credential can reach git through
  `values.yaml`.
- **Fail-fast for free (FR-010 / SC-008)** — this is the reason for `optional: false`. If the Secret
  or any referenced key is missing, the kubelet refuses to start the container with
  `CreateContainerConfigError` naming the missing key. **No application code change is needed to
  satisfy FR-010**, which matters because the backend's `settings.py` defaults `database_url` to `""`
  and would otherwise start happily and fail on first request (exactly SC-008's forbidden 0%-case).

**One URL serves both services.** Worth stating because it is not obvious: the backend rewrites
`postgresql://` → `postgresql+asyncpg://` and `sslmode=require` → `ssl=require` in
`settings.py:33-49`, while the frontend's `pg.Pool` (`lib/auth-server.ts:6-11`) consumes the URL
as-is with `rejectUnauthorized: false`. The **pooled** (`-pooler`) endpoint is therefore correct for
both, and matches the shape Phase III already uses. Both services genuinely need it — the frontend
holds Better Auth's session/user tables directly (spec Dependency note).

---

### D6 — Configuration split: ConfigMap vs Secret, and the two-value `BETTER_AUTH_URL` trap

Non-sensitive values go in a ConfigMap; credentials only in the Secret. The full matrix is in
[`contracts/env-contract.md`](./contracts/env-contract.md). The load-bearing entries:

| Variable | Consumed by | Value | Why |
|---|---|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | frontend **build** | `http://localhost:30800` | Baked into the browser bundle. Drives the one client-side direct call from `app/(protected)/tasks/[id]/edit/page.tsx` (FR-005). |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | frontend **build** | `http://localhost:30080` | Baked into the bundle; Better Auth's browser client signs requests with it. |
| `BETTER_AUTH_URL` | frontend **runtime** | `http://localhost:30080` | Better Auth server `baseURL`. **Must equal the browser-facing origin** or generated URLs and cookie scoping break. |
| `BETTER_AUTH_JWKS_URL` | backend runtime | `http://todo-chatbot-frontend:3000/api/auth/jwks` | **The trap.** The backend fetches JWKS over the pod network. Pointing `BETTER_AUTH_URL` at `localhost:30080` here would make the pod fetch from *itself* and fail. `jwt_validator.py:51` gives this variable priority, so setting it leaves `BETTER_AUTH_URL` free for the frontend. |
| `ALLOWED_ORIGINS` | backend runtime | `http://localhost:30080` | CORS for the direct browser→backend call. Already read from env (`settings.py:30`). |
| `DATABASE_URL` | both | Neon `phase-iv` pooled URL | Secret. |

**Note on `NEXT_PUBLIC_*` in the ConfigMap:** two of these are listed as *build* values. They are
deliberately **absent** from the runtime ConfigMap — placing them there would be misleading, since the
running container ignores them. The contract doc says so explicitly.

---

### D7 — Security posture: no cluster permissions at all

- **Dedicated ServiceAccount** per release with **`automountServiceAccountToken: false`**. Neither
  workload touches the Kubernetes API (the backend's agent uses in-process MCP tools and a database;
  see `backend-api/src/mcp/`), so the correct least privilege is *no* token and *no* RBAC objects.
  FR-017 is satisfied by construction rather than by a narrow Role.
- **Pod security context:** `runAsNonRoot: true`, `runAsUser: 1000`, `runAsGroup: 1000`,
  `seccompProfile: RuntimeDefault`.
- **Container security context:** `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`,
  `capabilities.drop: ["ALL"]`.
- **`readOnlyRootFilesystem` needs two writable scratch mounts:** an `emptyDir` at `/tmp` for the
  backend, and one at `/app/.next/cache` for the frontend. Without the latter Next.js fails on its
  first cache write. The backend also gets `PYTHONDONTWRITEBYTECODE=1` so Python does not try to write
  `__pycache__` into the read-only layer.
- **`runAsUser: 1000` on the backend needs no Dockerfile change:** `python:3.12-slim` ships its
  interpreter and site-packages world-readable and the app writes nothing, so a non-root UID can read
  everything it needs. Verified by the smoke step in the verification plan.

**Trade-off:** `readOnlyRootFilesystem: true` is the strictest setting and costs two `emptyDir`
volumes plus a bytecode env var. Accepted — it is a small, declarative price for removing the
container's ability to persist anything, and it is exactly what constitution V asks for.

---

### D8 — Probes, resource boundaries, and graceful scale-down

**Probes (FR-014).** The backend already exposes `GET /health` (`backend-api/src/main.py:39-41`), so
no code change is needed. The frontend has no health route; rather than add one, readiness uses an
HTTP GET of the public `/login` page (proves the Next server renders a real page, is unauthenticated,
and touches no database) with a `tcpSocket` liveness probe. **Provisional** — see Q8.

| Workload | liveness | readiness | startup |
|---|---|---|---|
| backend | `httpGet /health :7860` | `httpGet /health :7860` | `httpGet /health :7860`, 30 × 2s |
| frontend | `tcpSocket :3000` | `httpGet /login :3000` | `httpGet /login :3000`, 30 × 2s |

`/health` deliberately does **not** check the database. That is the behaviour SC-007 wants: with the
database unreachable, pods stay Ready rather than entering a restart loop, and the frontend shows an
error state instead of the whole app collapsing ("MUST surface an explicit, readable error rather than
restarting indefinitely with no diagnosable message").

**Resource boundaries (FR-015, SC-010)** — declared in `values.yaml`, overridable per service:

| Workload | requests | limits |
|---|---|---|
| backend | `100m` / `256Mi` | `500m` / `512Mi` |
| frontend | `100m` / `256Mi` | `500m` / `512Mi` |

SC-010 is proved by reading these **back from the cluster**, not by consumption metrics — so no
metrics addon is installed and none is assumed (matching the clarification recorded in the spec).

**Graceful scale-down (FR-013, User Story 3).** A chat turn is a long LLM call. Without protection, a
scale-down SIGTERMs an in-flight request mid-answer, and the spec's rule is that in-flight requests
must "either complete or fail cleanly — never be applied twice". Declarative fix, no code:

- `terminationGracePeriodSeconds: 60`
- a `preStop` hook (`sleep 10`) so the endpoint is withdrawn from Service rotation *before* the
  process begins shutting down, and `uvicorn`'s own graceful shutdown drains the rest.

Duplicate-application safety is already architectural: the backend holds no per-request state
(Assumption 4) and all task/conversation state is in PostgreSQL, so scaling changes nothing about
correctness. The plan's job is only to not interrupt work in flight.

**No leader election, no session affinity.** A single user's conversation could land on different pods
across turns; that is already correct because history is read from and written to the database, not
held in process memory. User Story 3's acceptance scenario 3 exists to *prove* this, not to add
mechanism.

---

### D9 — Observability and evidence (constitution IV, VII; FR-024/025/026/SC-011)

- **`docker ai` (Gordon) is used** for the container operations it supports (image build, Dockerfile
  review, image inspection) and is **named** in the quickstart (FR-025). It is present in this
  environment (`docker version 29.1.3`, `docker ai` responds). Where it cannot perform an operation,
  the documented fallback is the plain Docker CLI or Claude Code, and the substitution is recorded.
- **`kubectl-ai` and `kagent` are absent** from this environment and are treated as best-effort only.
  **No acceptance criterion depends on them**, and no in-cluster agent controller or observability
  stack is installed (FR-026).
- **Records under `history/`:** every AI-assisted operation goes to
  `history/prompts/local-kubernetes-deployment/`, which already exists (2 records), naming the
  assistant used. This satisfies FR-024/SC-011 and keeps phase evidence beside the Phase III records.
- **Verification (constitution VII):** every claim in the completion report is backed by a captured
  command and its output. A step that was only reasoned about is not reported as verified.

---

## Touch Points

### New files

| Path | Purpose |
|---|---|
| `frontend/Dockerfile` | Multi-stage Next.js standalone build (deps → builder → runner), non-root. |
| `frontend/.dockerignore` | **Security-critical.** Must exclude `.env*`, `node_modules`, `.next`. Without it the build bakes `frontend/.env` — auth secret and database URL — into the image, which the image scan in SC-004 would then catch. The spec names this exact hazard; `backend-api/.dockerignore` already handles it correctly on its side. |
| `charts/todo-chatbot/Chart.yaml` | Chart metadata. |
| `charts/todo-chatbot/values.yaml` | **Single source of truth** for ports, replica counts, images, resources, bounds. |
| `charts/todo-chatbot/templates/_helpers.tpl` | Name/label helpers so selectors stay consistent. |
| `charts/todo-chatbot/templates/serviceaccount.yaml` | ServiceAccount, `automountServiceAccountToken: false`. |
| `charts/todo-chatbot/templates/configmap.yaml` | Non-sensitive runtime config. |
| `charts/todo-chatbot/templates/backend-deployment.yaml` | Backend Deployment: probes, resources, security context, `secretKeyRef`s, `preStop`. |
| `charts/todo-chatbot/templates/backend-service.yaml` | NodePort `30800`→`7860`. Being a NodePort Service it also carries a ClusterIP, so the same object serves in-cluster DNS. |
| `charts/todo-chatbot/templates/frontend-deployment.yaml` | Frontend Deployment, as above. |
| `charts/todo-chatbot/templates/frontend-service.yaml` | NodePort `30080`→`3000`; its ClusterIP serves in-cluster DNS for the backend's JWKS fetch. |
| `charts/todo-chatbot/templates/NOTES.txt` | Post-install address summary. |
| `deploy/deploy.sh` (or `.ps1`) | The documented procedure: preflight → build → load → secret → helm → verify. |
| `deploy/preflight.sh` | The seven checks from D4, in isolation so they are runnable and testable alone. |
| `deploy/.env.deploy.example` | Committed **placeholder-only** template for the gitignored real file. |
| `README.md` (deployment section) | The clean-machine procedure (FR-021/022), including the rebuild-on-port-change warning. |
| `history/prompts/local-kubernetes-deployment/*` | AI-operation records (FR-024, SC-011). |

### Modified files (four small, each forced by a requirement)

| Path | Change | Forced by |
|---|---|---|
| `frontend/next.config.ts` | `output: 'standalone'` | Containerizing the Next server; packaging-level, no behaviour change. |
| `frontend/lib/auth-server.ts` | Make `trustedOrigins` env-driven (`ALLOWED_ORIGINS`), keeping the current values as defaults | **FR-007** — allowed origins must be deploy-time config and must not be embedded in the repository. See K1. |
| `frontend/lib/auth-server.ts` | Make `useSecureCookies` env-driven with the current production-derived default | Deployed scheme is plain HTTP; see K2. |
| `frontend/Dockerfile` → `next.config.ts` build args | Receive `NEXT_PUBLIC_*` as build args | FR-005/FR-006 — browser-facing addresses are build-time constants. |

**No change to:** `backend-api/Dockerfile`, any API contract, any route, any schema, any CRUD or agent
logic. FR-001's "no application behavior may be reimplemented" and FR-018/SC-006's preservation of
Phase III are satisfied by not touching them.

> **Correction to the table above:** the frontend Service maps NodePort **30080 → containerPort 3000**;
> the backend Service maps NodePort **30800 → containerPort 7860**. The one stray "30080→7860" line is
> a typo in this draft and is superseded by the D3 table.

### Reused unchanged from Phase III

- All frontend application source (`app/`, `components/`, `lib/` except the two lines in K1/K2), the
  Next.js 16.1.1 / React 19.2.3 stack, `proxy.ts` (Next 16's renamed middleware), and the
  `app/api/auth/[...all]` Better Auth handler.
- All backend application source, `backend-api/Dockerfile`, `backend-api/.dockerignore`,
  `requirements.txt`, the FastAPI routers and the in-process MCP agent tools.
- The **entire API surface** — `/api/auth/*`, `/api/{user_id}/tasks`, `/api/chat/*`, `GET /health` —
  unchanged, which is what makes FR-018/FR-019 preservation verifiable by regression rather than by
  rewrite.
- The **existing Neon project** (a new branch on it, not a new provider or project).
- Existing env-var *names* (`DATABASE_URL`, `BETTER_AUTH_SECRET`, `ALLOWED_ORIGINS`, `COHERE_API_KEY`,
  `NEXT_PUBLIC_BACKEND_URL`, …) — no renaming, so Phase III's `.env` remains the template for
  `.env.deploy`.
- Phase III `history/` records and the existing spec directories.

---

## Constitution Check

*GATE: evaluated before design (above) and re-evaluated after design (bottom).*

| Principle | Status | Evidence |
|---|---|---|
| **I. Declarative & Version-Controlled State** | ✅ PASS | Every workload, config, and exposure is a Helm template in git. The only non-file step is Secret *materialization*, done with `--dry-run=client -o yaml \| kubectl apply -f -`, which is idempotent and re-derivable from a gitignored source file — no live-cluster mutation is the delivery mechanism for a change. Diagnosis-time changes get back-ported. |
| **II. Reproducibility from a Clean State** | ✅ PASS | FR-021/FR-022 honoured: the procedure installs Minikube and Helm rather than assuming them (both confirmed absent here). Verified by SC-005's two consecutive clean-state runs. |
| **III. Environment Parity & Portability** | ✅ PASS | One chart, one artifact set; all environment difference is `values.yaml` + `.env.deploy`. No provider, cluster name, or host is assumed in a template — ports, images, replicas, and hosts are all values. FR-023 satisfied structurally. |
| **IV. AI-Assisted Operations with Captured Evidence** | ✅ PASS | Gordon used and named; `history/` records per operation; every AI-generated result confirmed by an independent observable check (the D3 post-build proof is one instance). |
| **V. Security & Configuration Hygiene** | ✅ PASS | Zero credentials in git, images, or logs: gitignored `.env.deploy` → Secret → `secretKeyRef`. `.dockerignore` on both services. `automountServiceAccountToken: false`, non-root, read-only rootfs, all capabilities dropped. Credentials rotate without a rebuild (FR-008) because they are runtime env, not build args. |
| **VI. Operational Readiness** | ✅ PASS | Every workload declares probes, resource requests/limits, and restart behaviour; `kubectl logs`/`describe`/`get` work without touching the workloads (SC-010). |
| **VII. Verification & Evidence Discipline** | ✅ PASS | The verification plan maps every acceptance criterion to a command; SC-005 requires two clean-state runs; results are recorded. |
| **VIII. Spec-Driven Traceability** | ✅ PASS | Every decision below cites an FR/SC/Assumption. Where the spec is silent, it is raised as an open question rather than invented. |

**Gate result: PASS — no violations, no Complexity Tracking entries required.**

---

### K1 — Frontend's `trustedOrigins` is hardcoded → required source change

`frontend/lib/auth-server.ts:51-55` currently reads:

```ts
trustedOrigins: [
  "http://localhost:3000",
  "https://q4-hackathon-2.vercel.app",
  ...(process.env.VERCEL_URL ? [`https://${process.env.VERCEL_URL}`] : []),
],
```

With the frontend exposed at `http://localhost:30080`, Better Auth will reject browser requests whose
`Origin` is not in this list — **sign-in fails**, and the symptom (a redirect loop or a 403 on
`/api/auth/*`) looks like an application bug rather than a configuration gap.

**Options:**

| Option | Assessment |
|---|---|
| **A. Make it env-driven** (recommended) | `trustedOrigins` derives from `ALLOWED_ORIGINS` (already the backend's variable name) with today's values as defaults. Satisfies FR-007's letter: origins become deploy-time config and leave the repository. |
| B. Pin the frontend NodePort to `3000` | Would match the hardcoded value with no source change. Requires `--extra-config=apiserver.service-node-port-range=3000-32767`, i.e. a non-default cluster shape. **Still violates FR-007's letter** (the origin remains committed in source) and trades a two-line config change for a non-portable cluster setting that constitution III disfavours. |

**Decision: Option A.** B is recorded because it is genuinely tempting — it keeps browser URLs
identical to Phase III — but it works *around* a stated requirement instead of meeting it, and it
couples the cluster to a non-default port range for no functional gain.

---

### K2 — `useSecureCookies` under plain HTTP

`frontend/lib/auth-server.ts:44` sets `useSecureCookies: process.env.NODE_ENV === "production"`. The
container runs `NODE_ENV=production`, so session cookies will carry the `Secure` attribute while the
app is served over `http://localhost:30080`.

Modern Chrome and Firefox treat `http://localhost` as a secure context and **do** accept `Secure`
cookies there, so this will very likely work as-is. But "very likely, on some browsers" is not a
property to leave implicit in a deployment that must reproduce on a clean machine.

**Decision:** add an explicit env override (e.g. `BETTER_AUTH_SECURE_COOKIES`, defaulting to the
present production-derived behaviour so Phase III is unaffected) and set it to `false` for the Phase IV
values. Small, reversible, and it removes a browser-dependent failure mode from the critical path of
User Story 1 — which is the MVP.

**Verification:** the sign-in step in the verification plan is the check. If sign-in succeeds without
the override, K2 can be dropped; the plan keeps it because a silent cookie failure is expensive to
diagnose and cheap to prevent.

---

## Verification Plan

Every acceptance criterion maps to a command whose output is the evidence. `NS=todo-chatbot`,
`R=todo-chatbot`.

### Spec Acceptance Criteria

| # | Acceptance criterion | Command(s) | Pass condition |
|---|---|---|---|
| AC1 | Both images build | `docker build -f backend-api/Dockerfile -t todo-chatbot-backend:$TAG backend-api/`<br>`docker build -f frontend/Dockerfile --build-arg … -t todo-chatbot-frontend:$TAG frontend/` | both exit 0 |
| AC2 | `helm install` deploys both services, **zero manual `kubectl` edits afterwards** | `helm upgrade --install $R charts/todo-chatbot -n $NS --create-namespace --wait` | exits 0; `--wait` blocks on readiness. Evidence that nothing was hand-edited: `git status` clean and no `kubectl edit`/`apply` in the transcript. |
| AC3 | Both services Running **and** Ready | `kubectl -n $NS get pods -o wide` | every pod `Running`, `READY n/n` |
| AC4 | Chatbot reachable & functional from host browser | open `http://localhost:30080` → sign in → send "add a task to buy milk" | UI loads, auth succeeds, task appears in `/tasks` |
| AC4b | **The one client-side direct call path (FR-005)** | open `http://localhost:30080/tasks/<id>/edit`, save a change | the page's browser-side call to `http://localhost:30800` succeeds — this is the page that breaks if only the in-cluster address is right (spec Risk #2) |
| AC5 | Scaling via Helm values changes running pod count | `helm upgrade $R charts/todo-chatbot -n $NS --set backend.replicaCount=3`<br>`kubectl -n $NS get pods -l app.kubernetes.io/component=backend` | exactly 3 backend pods; **no other artifact edited** |
| AC6 | Killing a pod → automatic recreation | `kubectl -n $NS delete pod <backend-pod>`<br>`kubectl -n $NS get pods -w` | replacement reaches Ready with no manual step |
| AC7 | README reproduces from a clean cluster | follow `README.md` top to bottom on a deleted+recreated cluster | app reachable |

### Constitution / spec Success Criteria

| # | Criterion | Command(s) | Pass condition |
|---|---|---|---|
| SC-001 | Clean machine → working app, <60 min, no undocumented prerequisites | time the full README run on a machine without Minikube/Helm | <60 min wall clock, zero steps not in the README |
| SC-002 | Unplanned termination → healthy in ≤2 min, zero manual steps | `kubectl -n $NS delete pod -l app.kubernetes.io/component=backend`; time to `READY` | ≤120 s, no intervention |
| SC-003 | Replica change needs no other artifact edit | `git diff --stat` after AC5 | only the `--set` invocation; no file changed |
| SC-004 | **Zero credentials** in git-tracked files, git history, **and both images** | named scanner (see Q3):<br>`trufflehog git file://. --no-update`<br>`trufflehog docker --image todo-chatbot-backend:$TAG`<br>`trufflehog docker --image todo-chatbot-frontend:$TAG` | 0 verified findings in all three. `.env`/`.env.example` are untracked+gitignored and therefore out of scope per the spec's clarification — but the **image** scans must also be clean, which is what `frontend/.dockerignore` guarantees. |
| SC-005 | Full acceptance procedure passes twice, from clean state, reproducibly | `minikube delete && minikube start … --ports=…` then run the whole procedure; **twice** | both runs pass every row above |
| SC-006 | 100% of Phase III conversational capabilities intact | manually exercise create / view / update / complete / delete **by natural language**, plus resume a prior conversation | all five operations plus resumption behave as in Phase III, no regression |
| SC-007 | Backend unavailable → loading/error state, auto-recovery **without restart** | `kubectl -n $NS scale deploy/$R-backend --replicas=0`; load the UI; then scale back to 1 | UI shows loading/error and does **not** crash; recovers on its own. Also confirm the frontend pod's `RESTARTS` stayed `0` — that is the "without a restart" evidence. |
| SC-008 | Missing required config → refuse to start, naming the item; 0% start-then-fail | `kubectl -n $NS create secret generic tmp --from-literal=WRONG=1 --dry-run=client -o yaml \| kubectl apply -f -`; point one `secretKeyRef` at a nonexistent key (or delete a key from the Secret) and re-apply | pod reports `CreateContainerConfigError` / `CreateContainerConfigError: secret "todo-chatbot-secrets" not found` **naming the missing key**; the container never runs |
| SC-009 | Re-run → in-place update, zero duplicates, zero orphans | `helm upgrade --install … ` again, then<br>`kubectl -n $NS get deploy,svc,cm,sa`<br>`helm -n $NS history $R` | resource counts equal the declared set; `history` shows revision 2 as `deployed`; revision 1 `superseded` |
| SC-010 | Status, logs, resource usage retrievable **without restarting/modifying** | `kubectl -n $NS get pods`<br>`kubectl -n $NS logs deploy/$R-backend --tail=50`<br>`kubectl -n $NS logs deploy/$R-frontend --tail=50`<br>`kubectl -n $NS get deploy -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.template.spec.containers[*].resources}{"\n"}{end}'` | probes stay green; declared requests/limits read back for **both** services. No metrics addon needed. |
| SC-011 | Every container operation attributable to a `history/` record naming the assistant | inspect `history/prompts/local-kubernetes-deployment/`; count operations in the transcript | one record per operation, assistant named, Gordon included |

### FR-specific checks not covered above

| Ref | Check | Command | Pass condition |
|---|---|---|---|
| FR-006 / FR-028 | **Collision is refused with the value named** | with the app installed, run `deploy/preflight.sh` after pointing a second release at `nodePort: 30080` | exits non-zero; stderr names the port **and** the owning Service; nothing was applied |
| FR-003 | Everything is declarative | `grep -rn "kubectl \(edit\|patch\|scale\)" deploy/ README.md` | no hits (or each hit documented as diagnosis-only with a back-port) |
| FR-008 | Credential rotation needs no rebuild | `kubectl -n $NS set env …`-free: re-create the Secret with a new `BETTER_AUTH_SECRET`, `kubectl rollout restart deploy` | workloads come up on the new value; **no image rebuilt** |
| FR-010 | (same as SC-008) | — | — |
| FR-011 | Frontend survives a not-yet-ready backend | delete the backend pod, immediately load the UI | loading/error state, no crash, auto-recovery |
| FR-013 | Scale up **and** down without loss/duplication | with 3 replicas, hold a multi-turn conversation that creates 1 task; scale to 1; scale back to 3; inspect `/tasks` and the conversation | exactly **one** task; conversation context intact |
| FR-014 | Ready-gating works | `kubectl -n $NS get endpoints $R-backend -o json` during a rollout | no endpoint listed until the pod is Ready |
| FR-017 | Least privilege | `kubectl -n $NS get pod <pod> -o jsonpath='{.spec.automountServiceAccountToken}{.spec.securityContext}{.spec.containers[*].securityContext}'`<br>`kubectl -n $NS auth can-i --list --as=system:serviceaccount:$NS:<sa>` | token not mounted; `runAsNonRoot`, dropped caps, read-only rootfs; **no** permissions listed |
| FR-023 | Environment difference is values-only | `helm template` with two different `values` files | identical object set; only values differ |
| FR-027 | Connection budget respected | `kubectl -n $NS get deploy $R-backend -o jsonpath='{.spec.replicas}'` vs the stated maximum; confirm the Neon limit | `8·B + 10·F` stays under the Neon limit with headroom — **maximum must be stated in the README once Q2 is answered** |
| Constitution I | Secret materialization is idempotent, not a mutation-as-delivery | run the `create secret … \| kubectl apply -f -` line twice | second run reports `unchanged`; no duplicate |
| Constitution II | Addons are self-enabled | fresh `minikube delete && minikube start` then the procedure | passes with **no addon** enabled — this plan requires none (NodePort, not Ingress; SC-010 forbids needing a metrics addon) |

### Cross-cutting regression

Phase III behaviour must be untouched. Because no application logic changes, the regression surface is
narrow: run the existing backend test suite (`backend-api/tests/`) before and after packaging, and
diff the results. Any difference is a real finding, not an expected consequence of deployment.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-local-kubernetes-deployment/
├── spec.md              # Input (finalized, clarified)
├── plan.md              # This file
├── research.md          # Phase 0 — decisions already resolved by recon
├── data-model.md        # Phase 1 — deployment entities and their invariants
├── quickstart.md        # Phase 1 — the documented procedure (FR-021/022)
├── contracts/
│   ├── env-contract.md      # Per-service environment variable matrix
│   ├── values-contract.md   # Helm values interface + invariants
│   └── deploy-cli-contract.md # Procedure CLI, exit codes, error taxonomy
├── checklists/
│   └── requirements.md  # Existing spec-quality checklist
└── tasks.md             # Phase 2 (/sp.tasks — NOT produced here)
```

### Source Code (repository root)

```text
phase-4-local-kubernetes-deployment/
├── backend-api/                  # REUSED — one existing Dockerfile, no source change
│   ├── Dockerfile                # reused as-is (port 7860)
│   ├── .dockerignore             # reused as-is (already excludes .env*)
│   └── src/                      # unchanged
├── frontend/                     # REUSED + packaged
│   ├── Dockerfile                # NEW — multi-stage, standalone, non-root
│   ├── .dockerignore             # NEW — security-critical
│   ├── next.config.ts            # MODIFIED — output: 'standalone'
│   ├── lib/auth-server.ts        # MODIFIED — env-driven origins; secure-cookie override
│   └── app/ components/ lib/     # unchanged
├── charts/
│   └── todo-chatbot/             # NEW — one chart, two workloads
│       ├── Chart.yaml
│       ├── values.yaml           # single source of truth for ports/replicas/images
│       └── templates/            # sa, cm, 2 deployments, 2 services, NOTES.txt
├── deploy/
│   ├── preflight.sh              # NEW — the seven checks (FR-028)
│   ├── deploy.sh                 # NEW — build → load → secret → helm → verify
│   └── .env.deploy.example       # NEW — placeholder template (real file is gitignored)
├── README.md                     # MODIFIED — the clean-machine procedure
├── history/prompts/local-kubernetes-deployment/   # AI-operation records
└── specs/004-local-kubernetes-deployment/         # this feature's artifacts
```

**Structure decision:** the existing web-application layout (sibling `frontend/` and `backend-api/`)
is preserved exactly; packaging is added *beside* each service and cluster artifacts are grouped under
a new top-level `charts/` and `deploy/`. No application directory is restructured, which keeps the
"re-host, don't rebuild" claim (SC-007) inspectable from the diff.

---

## Risks and Mitigations

| Risk | Mitigation | Verified by |
|---|---|---|
| **Stale frontend bundle** — a port changed but the image was not rebuilt; looks like an app bug (spec Risk #1) | Single-source ports (D3) + post-build `grep` proof + preflight check 7 + a warning block in the quickstart | D3 layer 3; AC4b |
| **The one client-side backend call path** breaks while everything else looks fine (spec Risk #2) | Dedicated verification row AC4b, exercised through the real page | AC4b |
| **`frontend/.env` baked into the image** — auth secret and DB URL leak, SC-004 fails (spec Risk #3) | `frontend/.dockerignore` must exist and exclude `.env*` **before** the first build; the SC-004 image scan proves it | SC-004 |
| **Secret sprawl across two services** — values drift, one service fails looking like an app bug | One Secret, one `.env.deploy`, a single documented env-contract matrix; both services consume the same keys | `contracts/env-contract.md`; SC-008 |
| **`--ports` unsupported by the driver** → no host path | Documented `kubectl port-forward` fallback publishing the **same** port numbers, so the built image stays valid | README; AC4 |
| **Backend cannot reach frontend for JWKS** → every authenticated request 401s | `BETTER_AUTH_JWKS_URL` set explicitly to the in-cluster Service DNS, taking priority over `BETTER_AUTH_URL` (D6) | SC-006 / chat round-trip |
| **`trustedOrigins` rejects the browser origin** → sign-in fails | K1 (env-driven origins) | AC4 |
| **`Secure` cookie over HTTP** → session never persists | K2 (explicit override) | AC4 |
| **Connection-budget exhaustion under scaling** (FR-027) | Formula `8·B + 10·F` stated in the README with a declared maximum, pending Q2 | FR-027 row |
| **`.env.example` holds live-looking credentials** (already flagged in the spec checklist) | Untracked + gitignored, so SC-004 is clean today; `.dockerignore` keeps it out of images. Recommend sanitizing to placeholders and **rotating** the values | SC-004; Q7 |
| **Minikube/Helm absent** (confirmed) and part of the documented procedure | Preflight *guides* installation rather than blocking; the 60-min budget includes it | SC-001 |

---

## Open Questions — spec silences

Flagged rather than guessed, per the constitution's rule that a missing requirement means stopping to
fix the spec. Each needs an owner decision before `tasks.md`. **None blocks writing `tasks.md` for the
other workstreams**, but Q1–Q3 do gate the script and the verification rows that reference them.

| # | Question | Options | Impact if unanswered |
|---|---|---|---|
| **Q1** | **How is the Neon branch provisioned?** The spec requires a dedicated branch (FR-020) but names no mechanism, and `neonctl` is not installed here nor is a Neon MCP server available. | (a) install `neonctl`, script it; (b) one-time manual console creation, URL pasted into `.env.deploy`; (c) Neon REST API via `curl` with a PAT | The data-provisioning step of the procedure cannot be written or timed |
| **Q2** | **What is the Neon connection limit** for this project's plan? Needed to compute and *state* FR-027's maximum declared replica count. | Read from the Neon console (Settings → connection limits) | FR-027 cannot be satisfied — the spec requires the maximum to be stated |
| **Q3** | **Which credential scanner** proves SC-004? The spec mandates that one be named and installed by the procedure but does not name it. | (a) TruffleHog — one tool covering git history **and** both images via `trufflehog docker`; (b) gitleaks for the repo + a separate image scan; (c) `docker scout` | SC-004 has no executable command |
| **Q4** | **Are the four source changes acceptable?** `next.config.ts`, `auth-server.ts` ×2, plus two new frontend packaging files. Each is forced by an FR (K1, K2, D1) but they are still edits to application source in a phase whose headline is "re-host, not rebuild". | (a) accept all four; (b) accept only `next.config.ts` + Dockerfile, and solve origins by pinning the frontend NodePort to 3000 | Option (b) changes the port plan in D3 and leaves FR-007 partially unmet |
| **Q5** | **Which Minikube driver is authoritative?** This plan assumes `--driver=docker` (Docker Desktop 29.1.3 is present). | `docker` (assumed), `hyperv`, `virtualbox` | `--ports` is docker/podman-only; another driver forces the port-forward fallback as primary |
| **Q6** | **Is `minikube start --ports` acceptable**, or should the procedure use `kubectl port-forward` as primary? The spec's edge case anticipated a host-side process; `--ports` avoids one entirely. | (a) `--ports` primary, port-forward fallback (planned); (b) port-forward primary | Changes the procedure's first command and whether a long-running host process must be documented as a dependency |
| **Q7** | **Sanitize `backend-api/.env.example` and rotate?** It contains live-looking values. Untracked + gitignored, so SC-004 passes, but a stray `git add -f` would commit them. | (a) replace with placeholders and rotate the exposed credentials; (b) leave as-is | Low severity, but the values have now also been read into this session's context |
| **Q8** | **Frontend health probe shape?** The app has no health endpoint. | (a) `httpGet /login` + `tcpSocket` (planned, no source change); (b) add `app/api/health/route.ts` (one small file, cleaner semantics) | Affects whether the frontend needs a fifth source change |
| **Q9** | **Should the frontend's `pg` pool be lowered?** It currently uses `pg`'s default `max: 10` per pod (`lib/auth-server.ts:6-11`), which dominates the connection budget next to the backend's 8. | (a) leave default, cap replicas; (b) set an explicit smaller `max` (source change) | Changes FR-027's arithmetic and the declared maximum |
| **Q10** | **Where do the deploy scripts and README live, and PowerShell or Bash?** This is Windows; `deploy/` is planned at the phase root with a Bash script runnable from Git Bash. | (a) Bash at phase root (planned); (b) PowerShell; (c) both | Affects the filenames in the touch-point list and the quickstart's commands |

---

## Post-Design Constitution Re-check

Re-evaluated after Phase 1 design (data-model, contracts, quickstart). **Result: PASS — unchanged.**

The design added no new artifacts beyond those checked above, and the two design-level additions that
could have introduced violations were resolved in the constitution's favour:

- **The Secret** could have become a "manual cluster mutation". Resolved by generating it through
  `--dry-run=client -o yaml | kubectl apply -f -` (principle I) while keeping credentials out of git
  (principle V).
- **The `preflight` script** could have become cluster-side machinery. It stays host-side read-only
  queries, so the workloads still need **no** Kubernetes API permissions (principles V and VI).

No Complexity Tracking entries were needed: nothing in this plan trades a principle for convenience.

---

## Follow-ups (max 3, per the execution contract)

1. **Answer Q1–Q3 before `/sp.tasks`** — they gate the data-provisioning step, the stated replica
   maximum, and SC-004's executable command. Q4–Q10 can be decided during implementation.
2. **Sanitize and rotate the credentials in `backend-api/.env.example`** (Q7). Small, independent, and
   worth doing before packaging work begins so no later build can pick them up.
3. **Verify `minikube start --ports` on this host early** — it is the one structural assumption in the
   exposure design that could not be confirmed by documentation lookup in this session (web search was
   unavailable). The port-forward fallback exists precisely so this is a cheap check, not a redesign.

---

## ADR Candidates

The following decisions pass the three-part test (long-term impact, multiple viable alternatives,
cross-cutting):

- **Chart topology** — one chart owning both workloads vs. one per service (D2). This choice persists
  into Phase V's cloud deployment, where an umbrella/subchart split may become correct.
- **Exposure mechanism** — pinned NodePort reached at `localhost` via driver port mapping vs.
  port-forward vs. Ingress. It fixes the browser-facing contract for the whole phase and drives the
  build-time-constant constraint (D3).

> 📋 Architectural decision detected: **Helm chart topology and host exposure mechanism for the
> Phase IV deployment** — document reasoning and tradeoffs? Run `/sp.adr helm-topology-and-exposure`
>
> Not created automatically. Awaiting the owner's decision, per the constitution's requirement that
> ADRs are never written without consent.
