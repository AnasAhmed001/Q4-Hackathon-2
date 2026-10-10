# Tasks: Phase IV — Local Kubernetes Deployment of the Todo Chatbot

**Input**: Design documents from `specs/004-local-kubernetes-deployment/`
**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required for user stories)
**Branch**: `004-local-kubernetes-deployment`
**Release / namespace**: `todo-chatbot` · **Chart**: `charts/todo-chatbot/`
**Pinned ports**: frontend NodePort `30080`→`3000`, backend NodePort `30800`→`7860`

**Tests**: The spec does not request TDD and this is a deployment feature. Verification tasks below are
**spec acceptance checks**, not unit tests. They are *not* optional — constitution VII and FR-022 require
each claim to be backed by a captured command and its output.

**Status of this document**: every task is executable as written. Where the plan was silent or
contradictory, the task is marked **⚠️ AMBIGUOUS** or **⚠️ DECISION REQUIRED** with the options inline —
see [Flagged Ambiguities](#flagged-ambiguities). Nothing was silently guessed.

---

## Scope of this revision (2026-10-01)

**This is a hackathon learning project with a handful of test users, not a production system.** The task
list was cut to the shortest path that still demonstrates the deployment and satisfies the spec's headline
criteria. Task IDs of surviving tasks are unchanged, so references elsewhere stay valid; dropped IDs are
simply absent.

| Dropped | What it was | Coverage consequence (know this before T067) |
|---|---|---|
| **T010** | `deploy/reset-db.sh` + `neon.branch_id` guard | No scripted reset. SC-005 becomes **one** clean run from `minikube delete` (T065), not two consecutive runs. |
| **T028, T029** | FR-028 collision pre-flight | **FR-028 is not verified.** A second install on the same cluster is left to `helm`'s own failure. |
| **T057** | Values-only render diff | **FR-023 is not verified.** |
| **T059–T061** | `quickstart.md`, `data-model.md`, `values-contract.md`, `deploy-cli-contract.md` | These plan-named artifacts are not produced. `research.md` (T004) and `contracts/env-contract.md` (T006–T008) still are. |
| **T062** | Phase III regression before/after diff | **FR-018 is not verified.** No application logic changes, so the surface is narrow. |
| **T066** | Second consecutive clean-state run | SC-005's "twice" is waived — see T065. |
| **T068** | ADR surfacing | No ADR for chart topology / exposure mechanism. |

**Two items were rewritten rather than dropped:**

- **T041** — the connection-budget derivation (`8·B + 10·F ≤ 901`) is demoted to a **footnote**. The
  stated maximum is now based on what the Minikube node actually allocates, which is the binding
  constraint on a laptop.
- **T064** — the credential scan now uses **no new tool installs**: `docker save` + grep for the images,
  `git grep` + `git log -p` for tracked files and history.

**And one requirement is deviated from by owner decision — not a scope cut, so it is listed separately:**

- **FR-020** — *"Phase IV MUST target a separate database or branch dedicated to this phase, so that
  verification runs are repeatable and non-destructive against Phase III data."* The owner chose the
  **existing database on the `main` branch**, so both halves fail: the deployment targets the shared
  database, and browser activity during T036–T049 mutates live Phase III rows. **T067 must report FR-020
  as NOT SATISFIED**, with the reason, and must not fold it in with the dropped-task waivers above. The
  trade-off is accepted at hackathon scale — a handful of test users, no production load, no purge to run
  — and it removes an entire provisioning step. See T009.

---

## Two findings from the pre-flight source re-verification (2026-09-24)

Both were called out as unresolved in the plan's Open Questions and were re-verified against the actual
Phase III source before writing a single task. **Both assumptions hold — confirmed, not assumed:**

| Assumption | Verdict | Evidence (verified) |
|---|---|---|
| **The frontend needs direct database access** | ✅ **CONFIRMED** | `frontend/lib/auth-server.ts:6-11` builds `new Pool({ connectionString: process.env.DATABASE_URL })` and passes it as `database: pool`. Better Auth's user/session tables live in Postgres. `DATABASE_URL` is therefore a **frontend runtime** Secret key, not backend-only. |
| **The frontend needs a second exposed backend port** | ✅ **CONFIRMED** | `frontend/lib/api-client.ts:31` reads `process.env.NEXT_PUBLIC_BACKEND_URL`. Its **only** importer is `frontend/app/(protected)/tasks/[id]/edit/page.tsx:5`, a `'use client'` component — so this call runs **in the browser** and needs a host-reachable backend address. This is FR-005, and it is exactly the "one client-side call path" of spec Risk #2. No second path exists. |

**Two additional findings not anticipated by the plan:**

1. **`frontend/lib/api-client.ts:31` falls back to `http://localhost:8000`** — but the backend container
   listens on **7860** (`backend-api/Dockerfile`, `CMD uvicorn ... --port 7860`). If
   `NEXT_PUBLIC_BACKEND_URL` is *not* baked at build time, the edit page silently calls a dead port.
   Handled by T034/T037.
2. **`frontend/.env` exists on disk (384 bytes) and is gitignored** via `frontend/.gitignore:34` (`.env*`).
   SC-004 is clean today, but a frontend image built without a `.dockerignore` would bake the auth secret
   and database URL into a layer. This is spec Risk #3, and T013 is the mitigation. **T013 must land before
   T031.**

## Plan documents that do not exist yet

`plan.md`'s Project Structure section lists `research.md`, `data-model.md`, `quickstart.md`, and
`contracts/{env,values,deploy-cli}-contract.md` as existing artifacts. **None of them exist** —
`find specs/004-local-kubernetes-deployment -type f` returns only `spec.md`, `plan.md`, and
`checklists/requirements.md`. Plan D6 says "the full matrix is in `contracts/env-contract.md`", and it is
not. Per the scope revision above, only `research.md` (T004) and `contracts/env-contract.md` (T006–T008)
are created; the rest are not produced.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: `[US1]`–`[US4]`, mapping to spec.md's prioritized user stories
- Every task names the `FR-###` / `SC-###` it satisfies, and a **Done when** line giving the exact
  command or observation that proves it — so it can be checked off against the spec, not against judgment

## Path Conventions

Paths are relative to the phase root `phase-4-local-kubernetes-deployment/`. Existing services keep their
sibling layout (`frontend/`, `backend-api/`); new cluster artifacts go in `charts/` and `deploy/`.
**No application directory is restructured** — that is what keeps SC-007's "re-host, not rebuild" claim
inspectable from the diff.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the baseline facts and decisions every later task depends on. Nothing here mutates
the cluster.

- [x] T001 Record the toolchain baseline for this host in `specs/004-local-kubernetes-deployment/research.md` — satisfies FR-021, FR-022, SC-001
      **Done when**: `research.md` exists with a table of `docker`, `docker ai`, `minikube`, `helm`, `kubectl` × {present/absent, version}. Baseline already observed: `docker 29.1.3` ✅, `docker ai` ✅ (rejects `--version` but parses flags), `kubectl v1.34.1` ✅, **`minikube` absent ❌, `helm` absent ❌**. The two absences are what make installing them a *procedure step* rather than a prerequisite (FR-021). `neonctl` is deliberately not tracked — it is not to be installed (T009).

- [x] T002 ✅ **DONE 2026-09-24** Resolve the `.specify` scripts' specs-root mismatch so later `/sp.*` commands work from this phase root — no FR; blocks tooling only
      **Problem**: both scripts resolve the specs root from `git rev-parse --show-toplevel`, which in this repo is the **parent** directory, so `check-prerequisites.sh` exited 1 with `Feature directory not found`.
      **Resolution**: a directory **junction** (a real link, proven by writing a probe file through it and reading it back from the target) at `Q4-Hackathon-2/specs/004-local-kubernetes-deployment` → this phase's real feature directory. A native symlink was unavailable — `MSYS=winsymlinks:nativestrict ln -s` returns "Operation not permitted" with Developer Mode off — and `New-Item -ItemType Junction` needs no elevation. **Re-verified 2026-10-01**: `LinkType = Junction`, target intact.
      **🔴 Why not a bare link of `specs/` itself.** `phase-4/specs/` also contains byte-identical copies of `001-task-management-api`, `001-todo-ai-chatbot` and `003-frontend-todo-app`. Linking the whole directory would let a run on a `001-*`/`003-*` branch resolve to **this phase's copy** — turning a loud failure into a *silent* wrong-tree read. The junction exposes only `004-*`, closing that hazard.
      **⚠️ What it does NOT isolate, measured.** All four phases share one repo and one branch, and the scripts derive the feature from the **branch, not the directory** — so while on branch 004, phases 2 and 3's own script copies also exit 0, resolving to *this* phase's `FEATURE_DIR`. On any other branch they fail loudly as before, and no phase-1/2/3 file is read or written.
      **Done when**: `cd phase-4-local-kubernetes-deployment && bash .specify/scripts/bash/check-prerequisites.sh --json` exits 0 and prints the absolute `FEATURE_DIR`, and the same for `setup-plan.sh`. — ✅ **VERIFIED**.

- [x] T003 [P] Create the directory skeleton `charts/todo-chatbot/templates/` and `deploy/` — satisfies FR-002, FR-003
      **Done when**: `ls charts/todo-chatbot/templates deploy` lists both directories.

- [x] T004 Answer and record the plan's open questions in `research.md` — **Q1–Q3 are closed**; Q4–Q10 remain as implementation detail
      **Q1 — RESOLVED**: the database is reached through the **Neon MCP server**, never `neonctl` and never the console, and it is the **existing database on the `main` branch** — no `phase-iv` branch is created. See T009, which records the resulting **FR-020 deviation** explicitly. **No decision remains open here.**
      **Q2 — RESOLVED (owner, 2026-10-01): the Neon connection limit is 901**, read as `SHOW max_connections` on the compute's **direct** Postgres endpoint in the SQL Editor. It is not a pooled-only number and there is no separate direct-endpoint contrast to check. The replica maximum is **not** derived from it — it is derived from the Minikube node (T041), with `8·B + 10·F ≤ 901` kept as a secondary footnote.
      **Q3 — RESOLVED (owner, 2026-10-01): no credential scanner is installed.** SC-004 is proven with tools already present — `docker save` + grep for the images, `git grep` + `git log -p` for tracked files and history. TruffleHog, gitleaks and `docker scout` are all **out**. See T064.
      **Done when**: `research.md` exists and records Q1–Q3 as above (copied from T009, T041 and T064 — not recomputed here), plus answers for **Q4–Q10** as they are settled during the work. **None of Q1–Q3 gates anything** — T041 and T064 carry their answers inline. A note records that plan.md still shows Q2/Q3 as open: it is the planning session's frozen record, and this document supersedes it.

- [x] T005 Sanitize the credentials in `backend-api/.env.example` to placeholders — satisfies FR-007, SC-004, constitution V (plan Q7)
      **✅ RESOLVED 2026-10-01 — sanitize-only; rotation is not required by this task.** The file contained a live-looking Neon `DATABASE_URL` and a Gemini API key and has been rewritten to placeholders.
      **Finding that lowers the stakes, measured**: `backend-api/.env.example` is **untracked and gitignored** (`backend-api/.gitignore:15`), and `git ls-files` confirms it is not in the index — so those values were **never committed and are not in git history**. This is a smaller problem than plan Q7 assumed. Rotating the credentials is now a judgement call for the owner, not a task dependency; T064's history scan is the check that proves nothing reached git.
      **Done when**: every env template in the repo contains placeholders only, and `git check-ignore -v` confirms each is ignored — so a stray `git add -f` is the only path to a real commit, and T026/T027 keep real values in `deploy/.env.deploy` instead.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Packaging, chart structure, configuration wiring, and the database. **⚠️ CRITICAL — no user
story can be exercised until this phase completes.**

### Contracts and configuration

- [x] T006 [P] Write `specs/004-local-kubernetes-deployment/contracts/env-contract.md` — the per-service environment variable matrix — satisfies FR-007, FR-008
      **Done when**: the file exists (it does not today, though plan D6 cites it) and lists, for every variable, its **consumer** (frontend-build / frontend-runtime / backend-runtime), its source (build-arg / ConfigMap / Secret), and its Phase IV value. It MUST include the D6 trap: `BETTER_AUTH_URL` is consumed by the **frontend** as `http://localhost:30080`, while the **backend** fetches JWKS from `BETTER_AUTH_JWKS_URL=http://todo-chatbot-frontend:3000/api/auth/jwks` — pointing the backend at `localhost:30080` would make the pod fetch from itself and 401 every request. It MUST also state that `NEXT_PUBLIC_*` values are **build-time** and deliberately absent from the runtime ConfigMap.

- [x] T007 [P] Record the FR-005 verification (client-side direct backend call) into the env contract with its file:line evidence — satisfies FR-005, spec Risk #2
      **Verdict already reached and recorded above: CONFIRMED.** `frontend/lib/api-client.ts:31` → sole importer `frontend/app/(protected)/tasks/[id]/edit/page.tsx:5` (`'use client'`).
      **Done when**: the env contract names the single path with both file:line references, records that **no second path exists**, and flags the `localhost:8000` fallback-vs-7860 mismatch as a hazard on that page.

- [x] T008 [P] Record the frontend direct-database-access verification into the env contract — satisfies **FR-020's direct-access clause only**; its *dedicated-branch* clause is deviated, see T009 — plus the spec Dependency note
      **Verdict already reached and recorded above: CONFIRMED.** `frontend/lib/auth-server.ts:6-11`. **Scope note**: FR-020 has two clauses. This task covers *"both the frontend and the backend connect to it directly"* and *"the same schema"* — both hold. It does **not** cover *"a separate database or branch dedicated to this phase"*, which the T009 decision deliberately deviates from. Do not let this task's green tick be read as FR-020 satisfied overall.
      **Done when**: `DATABASE_URL` appears as a **frontend runtime** Secret key in the env contract with the file:line evidence, and the contract states that both services consume the same URL (the backend rewrites `postgresql://`→`postgresql+asyncpg://` and `sslmode=require`→`ssl=require` in `settings.py`; the frontend's `pg.Pool` consumes it as-is).

### Database

- [x] T009 Point the deployment at the **existing** Neon database on the **`main`** branch — ✅ **DECIDED 2026-10-01 (owner): "use the same branch which is the main branch."** No `phase-iv` branch is created, and nothing is provisioned.
      **🔴 This is a recorded deviation from FR-020 — not a compliant choice, and not a silent one.** FR-020 requires Phase IV to "target a separate database or branch dedicated to this phase, so that verification runs are repeatable and non-destructive against Phase III data." **`main` is not that.** **T067 must report FR-020 as NOT SATISFIED** — not as passed, and not left unmentioned. What actually follows:
      - The deployment reads and writes **the same database the Phase III deployment uses**, which holds **104 rows** across 8 tables (`message` 64, `conversation` 17, `task` 9, `session` 5, `account` 4, `user` 4, `jwks` 1 — measured 2026-09-24).
      - **Browser activity during T036–T049 writes into that live data.** Signing in, sending chat messages and creating tasks all mutate Phase III's rows. Treat the demo as operating on the real system, because it is.
      - Both deployments share **one JWT keypair** in `jwks`, so a token minted by either deployment validates against the other.
      - Verification is therefore **not** "repeatable and non-destructive against Phase III data" — both halves of FR-020's stated rationale fail together.
      - **Accepted trade-off, given the context**: this is a hackathon learning project with a handful of test users, no production-scale load, and no purge or reset to run. The deviation buys the removal of an entire provisioning step.
      **This supersedes the earlier "phase-iv branch only — never touch main" constraint.** That constraint was written for a **purge** operation (the old T009/T010 design) which this revision **withdrew in full** — there is no purge and no reset script, so it no longer describes anything that exists. Read it as history, not as a live rule; this paragraph is the live rule.
      **What this task now does — read-only, no writes:**
      1. Resolve the `DATABASE_URL` for `main` via the Neon MCP `get_connection_string` (`project_id: billowing-wind-59531724`, branch `main` = `br-snowy-surf-ahjdfzub`). The owner already holds this value in `backend-api/.env` and `frontend/.env`; the call exists to **confirm the Secret's value is the intended one**, not to discover it.
      2. **Assert the branch is `ready` before relying on it** — `main` was once observed `archived` and had to be woken. A sleeping branch surfaces as a connection failure at T035, not as an obvious "wake me" error, so check `current_state` here rather than debugging it later.
      **⛔ Not called**: `create_branch`, `get_default_branch`, `get_branch`, `update_branch` — all four existed only to create the `phase-iv` branch and are now moot. `reset_from_parent` is destructive (resets to the parent's HEAD) and is out of scope entirely. **No `destructiveHint: true` tool remains in this feature.**
      **Done when**: `research.md` records the decision verbatim as *"existing database on `main`; FR-020 deviated by owner decision"*, and the `DATABASE_URL` T027 puts in `todo-chatbot-secrets` is confirmed to resolve to `br-snowy-surf-ahjdfzub`. This task performs **no MCP write**.

### Packaging

- [x] T011 Add `output: 'standalone'` to `frontend/next.config.ts` — enables D1's multi-stage frontend image
      **Done when**: the key is present; `cd frontend && npm run build` exits 0 and produces `.next/standalone/`.

- [x] T012 [P] Create `frontend/Dockerfile` — multi-stage (deps → builder → runner), non-root — satisfies FR-001, FR-017
      **Done when**: `docker build -f frontend/Dockerfile -t todo-chatbot-frontend:dev frontend/` exits 0; the runner stage copies `public/`, `.next/standalone/`, `.next/static/` (standalone does **not** copy the latter two); `ENV PORT=3000` and **`ENV HOSTNAME="0.0.0.0"`** are set — without `HOSTNAME` the standalone server binds to the container hostname and is unreachable from the pod network; `USER node` is the final user; and devDependencies are installed **before** `NODE_ENV=production` is set.

- [x] T013 [P] 🔒 **Create `frontend/.dockerignore` excluding `.env*`, `node_modules`, `.next`** — satisfies SC-004, spec Risk #3, constitution V
      **Security-critical and ordered deliberately**: `frontend/.env` exists on disk right now (verified, gitignored). Building `frontend/Dockerfile` **before** this file exists bakes the Better Auth secret and the database URL into an image layer, which T064 catches and which may not be removable from the layer cache.
      **Done when**: the file exists and excludes at minimum `.env`, `.env.*`, `node_modules`, `.next`, `.git`; and `docker build -f frontend/Dockerfile ... frontend/` followed by `docker run --rm <img> sh -c 'ls -a | grep -c "^\.env"'` reports `0`. **This task MUST complete before T031.**

- [x] T014 [P] Create `charts/todo-chatbot/Chart.yaml` — satisfies FR-002
      **Done when**: `helm lint charts/todo-chatbot` is runnable and reports no error about chart metadata.

### Chart

- [x] T015 Create `charts/todo-chatbot/values.yaml` — **the single source of truth** for ports, replica counts, images, and resource boundaries — satisfies FR-006, FR-009, FR-015 (D3)
      **Done when**: the file declares `frontend.nodePort: 30080`, `frontend.containerPort: 3000`, `backend.nodePort: 30800`, `backend.containerPort: 7860`, `replicaCount` for both, image repositories/tags, and per-service `resources.requests`/`limits` (D8: `100m`/`256Mi` requests, `500m`/`512Mi` limits — **these request values are the input to T041's replica maximum**). It also declares `existingSecret` by name so **no credential can enter git through this file** (FR-007).

- [x] T016 [P] Create `charts/todo-chatbot/templates/_helpers.tpl` — satisfies FR-003
      **Done when**: name and label helpers exist and the standard Helm labels (`app.kubernetes.io/name`, `app.kubernetes.io/instance`, `app.kubernetes.io/component`) are emitted consistently enough that `kubectl get pods -l app.kubernetes.io/component=backend` selects exactly the backend pods (T046 depends on it).

- [x] T017 [P] Create `charts/todo-chatbot/templates/serviceaccount.yaml` with `automountServiceAccountToken: false` — satisfies FR-017 (D7)
      **Done when**: rendered output shows the ServiceAccount with the flag `false`, and **no Role/RoleBinding/ClusterRole exists anywhere in the chart** — the backend's agent uses in-process MCP tools (`backend-api/src/mcp/`) and touches no Kubernetes API, so least privilege here is *no token and no RBAC*.

- [x] T018 [P] Create `charts/todo-chatbot/templates/configmap.yaml` — non-sensitive runtime config — satisfies FR-007 (D6)
      **Done when**: rendered output contains the runtime keys from T006 — `BETTER_AUTH_URL=http://localhost:30080`, `BETTER_AUTH_JWKS_URL=http://todo-chatbot-frontend:3000/api/auth/jwks`, `ALLOWED_ORIGINS=http://localhost:30080`, `NODE_ENV` — and contains **no** `NEXT_PUBLIC_*` key and **no** credential.

- [x] T019 Create `charts/todo-chatbot/templates/backend-deployment.yaml` — satisfies FR-010, FR-013, FR-014, FR-015, FR-017
      **Done when**: rendered output has (a) `secretKeyRef` entries with **`optional: false`** for every key in T006 — this is what makes FR-010/SC-008 fail-fast work with **zero application code change**, because `settings.py` defaults `database_url` to `""` and would otherwise start happily and fail on first request; (b) probes `liveness`/`readiness`/`startup` all on `httpGet /health:7860` with startup `30 × 2s`; (c) resource requests/limits from values; (d) pod security context `runAsNonRoot`, `runAsUser: 1000`, `runAsGroup: 1000`, `seccompProfile: RuntimeDefault`; (e) container security context `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `capabilities.drop: ["ALL"]`; (f) an `emptyDir` at `/tmp` and `PYTHONDONTWRITEBYTECODE=1` (read-only rootfs otherwise breaks Python bytecode writes); (g) `terminationGracePeriodSeconds: 60` and a `preStop` `sleep 10` so in-flight chat turns are withdrawn from rotation before shutdown (FR-013).

- [x] T020 Create `charts/todo-chatbot/templates/frontend-deployment.yaml` — satisfies FR-010, FR-011, FR-014, FR-015, FR-017
      **Done when**: as T019, with these differences — readiness `httpGet /login:3000`, liveness `tcpSocket :3000`, startup `httpGet /login:3000` `30 × 2s`; an `emptyDir` at `/app/.next/cache` (without it Next.js fails on its first cache write under `readOnlyRootFilesystem`); and `useSecureCookies` supplied per T025.

- [x] T021 [P] Create `charts/todo-chatbot/templates/backend-service.yaml` — NodePort `30800`→`7860` — satisfies FR-004, FR-005, FR-006
      **Done when**: rendered output is a `NodePort` Service with the nodePort **read from values, never cluster-assigned**, and its ClusterIP serves in-cluster DNS as `todo-chatbot-backend`.

- [x] T022 [P] Create `charts/todo-chatbot/templates/frontend-service.yaml` — NodePort `30080`→`3000` — satisfies FR-004, FR-006
      **Done when**: as T021, and the Service's ClusterIP resolves as `todo-chatbot-frontend` — which is exactly the host the **backend's** JWKS fetch depends on (T018).

- [x] T023 [P] Create `charts/todo-chatbot/templates/NOTES.txt` — post-install address summary
      **Done when**: `helm install --dry-run` prints the two browser URLs (`http://localhost:30080`, `http://localhost:30800`) and the port-change-requires-rebuild warning.

### Required source changes (each forced by a requirement)

- [x] T024 Make `trustedOrigins` env-driven in `frontend/lib/auth-server.ts:51-55`, deriving from `ALLOWED_ORIGINS` with today's values as defaults — satisfies FR-007 (**plan K1**)
      **Why forced**: with the frontend exposed at `http://localhost:30080`, Better Auth rejects browser requests whose `Origin` is not in the hardcoded list — **sign-in fails** with a redirect loop or a 403 on `/api/auth/*`, which reads as an application bug rather than a configuration gap.
      **Done when**: no origin string is hardcoded in a way that FR-007 forbids; setting `ALLOWED_ORIGINS=http://localhost:30080` makes the deployed origin accepted. Plan option B (pinning the frontend NodePort to `3000` to match the hardcoded value) is recorded as **rejected** — it works around FR-007 and couples the cluster to a non-default port range.

- [x] T025 Make `useSecureCookies` env-driven in `frontend/lib/auth-server.ts:44` with the present production-derived default preserved — satisfies User Story 1 (MVP sign-in) (**plan K2**)
      **Why**: the container runs `NODE_ENV=production`, so session cookies carry `Secure` while the app is served over plain HTTP. `http://localhost` is a secure context in modern Chrome/Firefox so this will *very likely* work — but "very likely, on some browsers" is not a property to leave implicit in a deployment that must reproduce on a clean machine, and the failure is expensive to diagnose.
      **Done when**: an override (e.g. `BETTER_AUTH_SECURE_COOKIES`) exists, defaults to the current behaviour (Phase III unaffected), and is set to `false` in the ConfigMap. **If T036's sign-in succeeds without it, this change may be reverted** — record whichever way it goes.

### Secret wiring

- [x] T026 [P] Create `deploy/.env.deploy.example` (placeholder-only) and confirm `.env.deploy` is gitignored — satisfies FR-007, constitution V
      **Done when**: the example file contains placeholders only; `git check-ignore -v deploy/.env.deploy` exits 0; and `git status --porcelain` shows no real `.env.deploy`. Note this repo's root `.gitignore` lists only `.vscode/`, `.neon`, `.env.local`, `node_modules/` — **`deploy/.env.deploy` is not covered today** and must be added.

- [x] T027 Implement the Secret materialization step in `deploy/deploy.sh` — satisfies FR-007, FR-008, FR-010, SC-008, constitution I
      **Done when**: `kubectl -n todo-chatbot create secret generic todo-chatbot-secrets --from-env-file=.env.deploy --dry-run=client -o yaml | kubectl apply -f -` is the step; running it **twice** reports `unchanged` the second time (idempotent, not a duplicate, not a mutation-as-delivery); every key referenced by the two Deployments is present; and the Secret carries `DATABASE_URL` **for both services** per T008.

**Checkpoint**: Foundation ready — the chart renders, both images build, the database is pointed at, and
secrets are wired. User stories can now be exercised.

---

## Phase 3: User Story 1 — Bring the whole application up with one documented procedure (Priority: P1) 🎯 MVP

**Goal**: A developer on a clean machine and a clean cluster follows one documented procedure and reaches
a working, browser-accessible chatbot — signing in and managing tasks by natural language — served from
cluster workloads rather than host processes.

**Independent Test**: From a clean state (toolchain present, `minikube delete && minikube start`, no
release installed), execute the documented procedure exactly as written, then open `http://localhost:30080`,
authenticate, and complete one full conversational task operation. Fully delivers value on its own.

**Why P1**: This is the MVP, and it is the scenario that proves constitution II (reproducibility from a
clean state) and SC-007 (re-hosted, not rebuilt). Every later story depends on it being deployable.

### Procedure

- [x] T030 [US1] Create `deploy/deploy.sh` implementing the full documented procedure: build → load → secret → `helm upgrade --install` → verify — satisfies FR-021, SC-001
      **✅ RESOLVED 2026-10-01 — the scripts are Bash** (plan Q10). They run from Git Bash on this Windows host; PowerShell is not used. Keep the form consistent across `deploy.sh`, the helper commands in T031/T033, and the README.
      **Done when**: `deploy/deploy.sh` runs the sequence with no manual step; the install command is `helm upgrade --install todo-chatbot charts/todo-chatbot -n todo-chatbot --create-namespace --wait` — **one command for both fresh install and in-place update**, so FR-012/SC-009 need no "does a release exist?" branch; and the script is idempotent end to end.

- [x] T031 [US1] Build both images, with **Docker AI (Gordon, `docker ai`)** assisting where it can — satisfies FR-001, FR-025, SC-011, AC1
      **Must run after T013** (`frontend/.dockerignore`) exists.
      **Frontend build-arg injection reads ports out of `values.yaml`** (D3) rather than duplicating them: `FE_NP=$(awk '/^frontend:/{f=1} f&&/nodePort:/{print $2; exit}' charts/todo-chatbot/values.yaml)`, likewise `BE_NP`, then `--build-arg NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:${FE_NP}" --build-arg NEXT_PUBLIC_BACKEND_URL="http://localhost:${BE_NP}"`. The script cannot drift from the chart because it reads the chart. A parse failure **aborts** rather than silently baking `http://localhost:` into the bundle.
      **Done when**: `docker build -f backend-api/Dockerfile -t todo-chatbot-backend:$TAG backend-api/` and `docker build -f frontend/Dockerfile --build-arg ... -t todo-chatbot-frontend:$TAG frontend/` **both exit 0**; the Gordon operation (or the recorded fallback) is captured under `history/` naming the assistant used (SC-011).

- [x] T032 [US1] Load both images into Minikube — satisfies the spec edge case "application images not available to the cluster"
      **Done when**: `minikube image load todo-chatbot-backend:$TAG` and `... frontend:$TAG` succeed, and `minikube image ls | grep todo-chatbot` lists both. This is a **procedure step, not tribal knowledge** — a clean-state run otherwise fails at the least obvious point.

- [x] T033 [US1] Start Minikube with the docker driver, a stated resource allocation, and published ports; verify host reachability — satisfies FR-006, SC-001
      `minikube start --driver=docker --cpus=4 --memory=4096 --ports=30080:30080,30800:30800`
      **The `--cpus`/`--memory` values are a deliberate, documented choice, not a default** — they are the input to T041's replica maximum, so they must be stated here and reproduced in the README. Changing them changes the stated maximum; if you change them, say so in T041.
      **✅ RESOLVED 2026-10-01 — `--ports` works on the docker driver on this host. The fallback is NOT primary.** `docker inspect minikube --format '{{json .NetworkSettings.Ports}}'` shows `30080/tcp` and `30800/tcp` both published to `0.0.0.0` at the same numbers, and `curl http://localhost:30080/login` returns **200**. **Confirmed again on 2026-10-09 after a full Docker Desktop restart**: the port bindings live in the container's config and came back with it, so the primary mechanism survives a cluster restart — no host-side long-running process is required. Evidence: `research.md` §2 Q6 (original verification) and §5.8 (restart survival).
      **Original plan-time uncertainty, retained for the record (plan Q5/Q6, plan Follow-up 3)**: `--ports` support on the docker driver was **the one structural assumption in the exposure design that could not be confirmed by documentation lookup**. The plan chose `--ports` as primary with `kubectl port-forward` as documented fallback — a pinned, predictable `http://localhost` address with **no hosts-file entry and no extra long-running host process**. The fallback deliberately publishes the **same port numbers**, so the addresses baked into the frontend image stay valid either way. That hedge was cheap and correct to make; it simply turned out not to be needed.
      **Done when**: EITHER `curl -sS -o /dev/null -w '%{http_code}' http://localhost:30080/login` returns a non-error status... OR the driver rejects `--ports`, in which case the port-forward fallback is adopted as primary, its host-process dependency is **documented as a required step**, and the choice is recorded in `research.md`. **Do not proceed to T035 without a host-reachable frontend URL.**

- [x] T034 [US1] Post-build proof that the declared ports actually landed in the browser bundle — satisfies FR-005, FR-006, spec Risk #1 (D3 layer 3)
      `docker run --rm --entrypoint sh todo-chatbot-frontend:$TAG -c "grep -rq 'localhost:${BE_NP}' .next/static && echo BAKED_OK"`
      **This is the concrete mitigation for spec Risk #1** — the stale-bundle failure where a port changed but the image was not rebuilt, producing a symptom that looks like an application bug. Per the finding above, the hazard is sharper than the plan recorded: without this value baked, `api-client.ts` falls back to **`:8000`** while the backend listens on **7860**.
      **Done when**: `BAKED_OK` is printed for **both** `localhost:30080` and `localhost:30800`.

### Verification

- [x] T035 [US1] Install the release and confirm both services Running **and Ready** — satisfies FR-002, AC2, AC3
      **Done when**: `helm upgrade --install ... --wait` exits 0 (blocking on readiness); `kubectl -n todo-chatbot get pods -o wide` shows **every** pod `Running` with `READY n/n`. Evidence that no manual edit occurred: `git status` clean and no `kubectl edit`/`apply` in the transcript (FR-003).
      **✅ MET 2026-10-01.** `helm upgrade --install … --wait` **exit 0**, `STATUS: deployed`, `REVISION: 3`; both pods `1/1 Running`; `localhost:30080/login` → 200 and `localhost:30800/health` → 200.
      **⚠️ Two clauses of the done-condition are reported as-written rather than as-met:**
      1. **"`git status` clean" — not satisfiable, and not evidence of anything here.** The Phase IV deliverable *is* the uncommitted change set (`charts/`, `deploy/`, `frontend/Dockerfile`, the modified `backend-api/Dockerfile`, …), so a clean tree is the one state that would mean **nothing was delivered**. The clause is trying to prove *no hand-edited deployed resource*, which is genuinely proven a different way — see (2).
      2. **"no `kubectl … apply` in the transcript" — literally false, and correctly so.** `deploy.sh` applies two objects declaratively (`kubectl create namespace … --dry-run | kubectl apply -f -`, and the Secret). Both are **idempotent applies of generated manifests driven by the committed script**, which is what FR-003 asks for; the thing FR-003 forbids is a **hand-edit of a live resource**. **`kubectl edit` was never used**, and no object exists in the cluster that is not rendered by `charts/todo-chatbot` or built by `deploy/deploy.sh`. The `apply -f -` seen in the log is the declarative path working, not a deviation from it.
      **First attempt failed and is recorded rather than hidden** — `UPGRADE FAILED: Progress deadline exceeded` on the run that exposed the quoted-`DATABASE_URL` defect. Analysis in `research.md` §5.6, including why `--wait` failing there was the correct behaviour.

- [x] T036 [US1] End-to-end browser verification: sign-in, then one full conversational task operation — satisfies SC-006 (partial), AC4, and confirms T024/T025
      **Done when**: opening `http://localhost:30080` loads the UI, **authentication succeeds** (this is the check for the K1 origins change and the K2 cookie change), and sending e.g. "add a task to buy milk" causes the task to appear in `/tasks`. If sign-in fails with a redirect loop or a 403 on `/api/auth/*`, the cause is `trustedOrigins` — not an application defect.
      **✅ MET 2026-10-10.** Owner-verified after the four-layer fix chain (research.md §5.10). Sign-in, task operations, and chatbot all working.

- [x] T037 [US1] **Verify the one client-side direct call path** — satisfies **FR-005**, spec Risk #2, AC4b
      **Requires its own explicit step**: this path fails *only* when a user opens one specific page, so a deployment can satisfy the in-cluster-address requirement completely and still leave this page broken.
      **Done when**: open `http://localhost:30080/tasks/<id>/edit`, save a change, and the page's browser-side call to `http://localhost:30800` succeeds — confirmed in the browser's network panel, not merely inferred. A call to `:8000` instead means the build args did not land (re-check T034).
      **✅ MET 2026-10-10.** Owner-verified. The client-side `api-client.ts` correctly uses `NEXT_PUBLIC_BACKEND_URL` (inlined as `localhost:30800`) for browser calls.

- [ ] T038 [US1] Verify the frontend survives a not-yet-ready backend and recovers without restart — satisfies FR-011, SC-007
      `kubectl -n todo-chatbot scale deploy/todo-chatbot-backend --replicas=0`, load the UI, then scale back to 1.
      **Done when**: UI shows a **loading or error state and does not crash**; it recovers on its own once the backend is reachable; and the frontend pod's `RESTARTS` stayed **`0`** — that last observation is the "without a restart" evidence.

- [x] T039 [US1] Verify stop/restart of the *cluster* returns to a working state — satisfies US1 acceptance scenario 4, spec edge case "cluster stopped and restarted"
      **Distinct from T065's clean state**: this is a **stopped-and-restarted** cluster, not a recreated one.
      **Done when**: `minikube stop` then `minikube start` (plus re-establishing host reachability per T033) yields a working application **without re-running the build or re-installing from scratch**; the command used is exactly the one in the README.
      **✅ MET 2026-10-09.** Both restarts exercised — (a) Docker Desktop restarted after 8 days down, and (b) the literal `minikube stop` → `minikube start`. Each time: pods returned `1/1 Running`, both NodePorts answered **200**, and helm stayed at **`REVISION: 3` / `STATUS: deployed`** — **no image rebuild and no reinstall**. The published ports survived because the bindings live in the container's config. Full evidence in `research.md` §5.8.
      **⚠️ The first reading of this test was discarded.** `kubectl wait --for=condition=available` returned **"condition met" while both apps were down**, because it read a **stale `Available=True`** from 8 days earlier that the restarted controller had not yet reconciled — and the ports answered `000`. A naive automated check would have passed on a dead cluster. Re-verified after reconciliation and **independently probed with `curl`**, which is what T039's behavioural done-condition actually requires.

- [ ] T040 [US1] Verify fail-fast on missing required configuration — satisfies FR-010, SC-008
      Delete a key from `todo-chatbot-secrets` (or point one `secretKeyRef` at a nonexistent key) and re-apply.
      **Done when**: the pod reports `CreateContainerConfigError` **naming the missing item**, the container **never runs**, and this happens **100% of the time** — never a start-then-fail-on-first-request. Note that `settings.py` defaults `database_url` to `""`, so without `optional: false` the backend would start happily and fail later, which is exactly SC-008's forbidden case.

- [ ] T041 [US1] State the maximum declared backend replica count in the README, derived from the Minikube node — satisfies **FR-027**
      **The binding constraint is the node, not the database.** Each backend pod requests `100m` CPU / `256Mi` memory (D8, declared in T015). Scheduling is governed by **requests**, not limits, so the ceiling is:
      **`max_backends ≈ min( (allocatable_cpu − system − F·100m) / 100m , (allocatable_mem − system − F·256Mi) / 256Mi )`** — at `frontend.replicaCount = 1` (`F = 1`).
      **Read the real numbers, do not assume them**: `kubectl get node minikube -o jsonpath='{.status.allocatable}'`, then subtract the `kube-system` pods' requests. **Memory binds first**, roughly 10× sooner than CPU, so the stated maximum is a memory number.
      **Worked example at T033's stated allocation (`--cpus=4 --memory=4096`, `F=1`)** — arithmetic from the documented inputs, to be **replaced by the measured allocatable on the day, not carried forward as a result**: ~4096Mi allocatable, less ~300Mi of system pods, less 256Mi for the frontend ⇒ ~3540Mi for backends ⇒ **≈ 13 backend replicas**. CPU at the same point allows ~35. *The measured value supersedes this example; the README states the measured one.*
      **Footnote — the connection budget, secondary and non-binding.** `8·B + 10·F ≤ 901`, where 901 is the Neon compute's direct `max_connections` limit (owner-measured, T004). The operands are source-verified: backend `pool_size=3` + `max_overflow=5` = 8 (`backend-api/src/database.py:15-16`); frontend `pg-pool` default `max` = 10 (`frontend/node_modules/pg-pool/index.js:89`). At `F=1` this allows `B ≤ 111` — comfortably above the node-bound figure, which is why it is a footnote and not the basis of the stated maximum. Each frontend replica costs 10 connections ≈ 1.25 backend replicas, so `F` is stated alongside `B` rather than folded in.
      **Done when**: `kubectl -n todo-chatbot get deploy todo-chatbot-backend -o jsonpath='{.spec.replicas}'` is compared against the **stated maximum in the README**; the README states the measured maximum **and the `minikube start` allocation it assumes**, with the arithmetic shown and the connection budget as a footnote. If the arithmetic does not fit the declared count, lower the declared count.

**Checkpoint**: User Story 1 is complete and independently demonstrable — the application is running on
the cluster, browser-reachable, and the full procedure is documented. **This is the MVP.**

---

## Phase 4: User Story 2 — The platform self-heals from workload failure (Priority: P2)

**Goal**: A pod is deleted or a workload crashes; without any developer action the cluster recreates it
and the application serves requests again.

**Independent Test**: With the application healthy, terminate a running instance of each workload in turn;
observe replacement instances start automatically and the application serve requests again, with no manual
redeployment.

**Why P2**: This is the primary operational benefit of moving to a cluster, and the direct expression of
constitution VI and SC-002. Probes and `terminationGracePeriodSeconds` are already built in T019/T020 —
**this phase is verification**, because self-healing is a property of the Deployment controller rather
than new mechanism.

- [ ] T042 [US2] Verify backend termination → automatic recreation, no manual steps — satisfies **SC-002**, US2 acceptance scenario 1
      **Done when**: `kubectl -n todo-chatbot delete pod <backend-pod>` is followed by a replacement reaching `Ready` **within 120 s with zero manual steps**, and a chat round-trip succeeds afterwards. Time it — SC-002 states 2 minutes, and the timing is the evidence.

- [ ] T043 [US2] Verify frontend termination → automatic recreation — satisfies US2 acceptance scenario 2
      **Done when**: `kubectl -n todo-chatbot delete pod <frontend-pod>` is followed by a replacement reaching `Ready` automatically and `http://localhost:30080` being reachable again.

- [ ] T044 [US2] Verify readiness gating: traffic is not routed to an instance that cannot serve it — satisfies **FR-014**, US2 acceptance scenario 3
      **Done when**: `kubectl -n todo-chatbot get endpoints todo-chatbot-backend -o json` taken **during a rollout** lists **no endpoint address** until the pod is `Ready`, and lists it immediately after. The frontend's readiness is the `httpGet /login` probe, which proves the Next server renders a real page without touching the database.

- [ ] T045 [US2] Verify that a persistent failure surfaces a readable error rather than an indefinite restart loop — satisfies spec edge case "database unreachable, credentials invalid, or connection limit reached"
      **Done when**: with an unreachable database or invalid credentials, the workload surfaces an **explicit, readable error** rather than restarting forever with no diagnosable message. Note `/health` deliberately does **not** check the database — that is the behaviour SC-007 wants, keeping pods `Ready` so the frontend shows an error state instead of the whole app collapsing.

**Checkpoint**: User Stories 1 and 2 both work independently. Recovery is owned by the platform.

---

## Phase 5: User Story 3 — Scale the backend without breaking the chatbot (Priority: P3)

**Goal**: Changing the declared backend instance count changes the running instance count, and the chatbot
continues to behave correctly — requests spread across instances, conversation history stays consistent,
no task operation is applied twice.

**Independent Test**: Change only the declared replica count, apply it, confirm the running count matches,
then drive a conversational workload and confirm responses remain correct and no operation is duplicated.

**Why P3**: This validates that the Phase III architecture — stateless request handling, database-backed
conversation and task state — genuinely holds under a clustered deployment. `replicaCount` was already
declared configurable in T015 (FR-009), so **this phase is verification**; no leader election and no
session affinity are added, because history is read from and written to the database rather than held in
process memory.

- [ ] T046 [US3] Verify scale up 1→3 changes the running pod count with no other artifact edited — satisfies **SC-003**, US3 acceptance scenario 1
      `helm upgrade todo-chatbot charts/todo-chatbot -n todo-chatbot --set backend.replicaCount=3`
      **Done when**: `kubectl -n todo-chatbot get pods -l app.kubernetes.io/component=backend` reports **exactly 3** Ready backend pods, and `git diff --stat` shows **no file changed** — only the `--set` invocation. SC-003 requires the replica change to need no other artifact edit, so the clean diff *is* the criterion.

- [ ] T047 [US3] Verify scale down 3→1 leaves the chatbot functional — satisfies US3 acceptance scenario 2
      **Done when**: exactly 1 backend pod remains, and a chat round-trip still succeeds afterwards. The `preStop` hook and `terminationGracePeriodSeconds: 60` from T019 are what keep an in-flight LLM call from being SIGTERMed mid-answer — the spec requires in-flight requests to "either complete or fail cleanly — never be applied twice".

- [ ] T048 [US3] Verify multi-turn conversation correctness across pods, with exactly-once task application — satisfies **FR-013**, **FR-019**, US3 acceptance scenario 3
      **FR-019 belongs here rather than anywhere else**: "per-user data isolation and the existing authorization behavior MUST be preserved unchanged" is precisely what replication threatens — if any user-scoped state lived in process rather than in the database, two pods would leak across each other. This is the task that would catch it.
      **Done when**: with multiple backend replicas, a multi-turn conversation preserves context across turns, and each requested task operation is applied **exactly once** — confirmed by inspecting the resulting task list and the conversation. A single user's turns landing on different pods is *expected and correct*, not a defect. **Isolation check**: with two distinct signed-in users hitting different pods, neither user's `/tasks` list nor conversation history contains the other's rows.

- [ ] T049 [US3] Verify no data loss and no duplicates across a full scale cycle — satisfies FR-013, US3 acceptance scenario 4
      **Done when**: with 3 replicas, hold a conversation that creates exactly 1 task; scale to 1; scale back to 3; then inspect `/tasks` and the conversation and find **exactly one** task and an intact conversation. This is the check that would catch per-process state if the Phase III statelessness assumption (spec Assumption 4) were false.

**Checkpoint**: All three of US1–US3 work independently. Clustering is proven not to weaken correctness.

---

## Phase 6: User Story 4 — Inspect, operate, and update the deployment (Priority: P4)

**Goal**: Inspect the running application — health, logs, resource consumption for each workload; re-run
the deployment procedure to apply a change and have it update in place rather than create a second
conflicting installation; adjust declared resource boundaries.

**Independent Test**: With the application running, retrieve status, logs, and resource usage for both
workloads without restarting or altering them; then re-run the deployment procedure and confirm an
in-place update with no duplicated resources.

**Why P4**: Constitution VI requires status, logs, and resource boundaries to be observable and declared
for every workload. Probe and resource declarations already exist from T019/T020 — **this phase is
verification plus the update-path proof**.

- [ ] T050 [US4] Verify status retrieval without touching the workloads — satisfies **FR-016**, **SC-010**, US4 acceptance scenario 1
      `kubectl -n todo-chatbot get pods`
      **Done when**: health and readiness of **every instance of both services** is reported, and the probes stay green afterwards — proving the retrieval neither restarted nor modified anything.

- [ ] T051 [US4] Verify logs for both services are retrievable — satisfies FR-016, SC-010, US4 acceptance scenario 2
      `kubectl -n todo-chatbot logs deploy/todo-chatbot-backend --tail=50` and `... frontend --tail=50`
      **Done when**: both return log output **without restarting or modifying** the workloads, and the output contains **no credential values** (FR-007 forbids writing secrets to logs).

- [ ] T052 [US4] Verify declared resource boundaries read back from the cluster — satisfies FR-015, **SC-010**, US4 acceptance scenario 3
      `kubectl -n todo-chatbot get deploy -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.template.spec.containers[*].resources}{"\n"}{end}'`
      **Done when**: requests and limits are read back for **both** services. **SC-010 defines "resource usage" as declared boundaries read from the cluster — NOT live consumption metrics** — so **no metrics addon is installed and none is assumed present**. If this task finds itself reaching for `kubectl top`, the spec's clarification is being violated.

- [ ] T053 [US4] Verify re-running the procedure is an in-place update with zero duplicates and zero orphans — satisfies **FR-012**, **SC-009**, US4 acceptance scenario 4
      **Done when**: after re-running `deploy/deploy.sh`, `kubectl -n todo-chatbot get deploy,svc,cm,sa` returns **exactly the declared set** — zero duplicates, zero orphans — and `helm -n todo-chatbot history todo-chatbot` shows the new revision `deployed` with the previous one `superseded`. This is where `helm upgrade --install` being one command for both paths (T030) pays off.

- [ ] T054 [US4] Verify a changed declared resource boundary is adopted without removing and recreating the application — satisfies US4 acceptance scenario 5, FR-015
      **Done when**: after changing a boundary in `values.yaml` and re-running the procedure, the workload adopts the new boundary and a **rolling** update is observed — the application is not deleted and recreated. Note the spec also requires a temporarily mismatched frontend/backend pair to not corrupt data or leave the app permanently broken; the end state must be consistent and working.

- [ ] T055 [US4] Verify a credential is replaceable without rebuilding any image — satisfies **FR-008**
      **Done when**: re-creating `todo-chatbot-secrets` with a new `BETTER_AUTH_SECRET` and running `kubectl rollout restart deploy` brings both workloads up on the new value with **no image rebuilt**. Because credentials are runtime env rather than build args, this holds by construction — the task confirms it.

- [ ] T056 [US4] Verify every deployed artifact is declarative and no manual cluster mutation is the delivery mechanism — satisfies **FR-003**
      `grep -rn "kubectl \(edit\|patch\|scale\)" deploy/ README.md`
      **Done when**: no hits — or each hit is documented as **diagnosis-only with the change back-ported to source**. Any `kubectl scale` used for diagnosis in T038 or T044 must be recorded as such, since the *delivery* mechanism for a replica change is `values.yaml` (SC-003).

**Checkpoint**: All four user stories are independently functional. The deployment is operable, not merely
running.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T058 [P] Author the deployment section of `README.md` — the clean-machine procedure — satisfies **FR-021, FR-022, SC-001**, AC7
      **Done when**: the README takes a reader from a machine **without Minikube or Helm** to a running, browser-reachable application, top to bottom, with **zero undocumented prerequisites** — installing Minikube and Helm **is a step in it**, not an assumption, and the 60-minute budget includes them. It MUST also document:
      - the **port-change-requires-a-frontend-rebuild** warning (D3, in a warning block);
      - the `minikube start` allocation (T033) and the **stated maximum declared backend replica count** derived from it (T041), with the arithmetic, and the `8·B + 10·F ≤ 901` connection budget as a **footnote**;
      - the credential-scan commands from T064 — **no tool install is required**, so there is nothing to install and nothing to document as an install step;
      - the host-reachability mechanism chosen in T033 and its recovery path if that mechanism is a host-side process;
      - the `docker ai` (Gordon) naming from FR-025.
      **⚠️ Ordering trap**: this task is [P] only against T063. It must be **re-verified after T064 and T065**, because the clean-state run is what proves the README is complete — a README written but never followed is not evidence.

- [ ] T063 [P] Create `history/prompts/local-kubernetes-deployment/` records for every AI-assisted operation, naming the assistant used — satisfies **FR-024, SC-011**
      **Done when**: the directory contains one record per AI-assisted operation, the **Gordon** container operations are included and named, and any substitution for an unavailable tool (Gordon, `kubectl-ai`, `kagent`) is recorded with the reason. `kubectl-ai` and `kagent` are absent from this host and are best-effort only — **no acceptance criterion may depend on them** (FR-026).

- [ ] T064 🔒 **Credential scan over tracked files, git history, and both built images — with no new tool installs** — satisfies **SC-004**
      **✅ RESOLVED 2026-10-01 — no scanner is installed.** Only `git`, `grep`, `tar` and `docker` are used; all are already present. **TruffleHog is not selected and must not be installed**; gitleaks and `docker scout` are equally out (repository-only, and CVEs-not-credentials, respectively).
      **Scope, per the spec's clarification**: "the repository" means **git-tracked files and git history**. Untracked working-tree files — notably `.env`, `frontend/.env` and `backend-api/.env.example`, all verified gitignored — are explicitly **out of scope**. **Both built images are in scope.**
      **Patterns to search for** — both the generic shapes and **the project's actual values**, which are the ones that matter: the Neon password from the current `DATABASE_URL`, the `GEMINI_API_KEY`, `BETTER_AUTH_SECRET`, and any `postgresql://user:pass@` URL. Use `grep -F` for literal values (they contain regex metacharacters) and `-E` for the generic patterns (`AIza[0-9A-Za-z_-]{35}`, `npg_[A-Za-z0-9]{8,}`, `postgres(ql)?://[^:]+:[^@]+@`, `sk-[A-Za-z0-9]{20,}`, `-----BEGIN [A-Z ]*PRIVATE KEY-----`).
      1. **Tracked files**: `git grep -nIE '<patterns>'` and `git grep -nF -- '<value>'`. Also `git ls-files -z | xargs -0 grep -lIE '<patterns>'` for anything `git grep` skips.
      2. **History**: `git log -p --all | grep -nIE '<patterns>'`, and `git log --all -S'<value>' --oneline` for each literal value — `-S` finds the commit that introduced it even if later deleted.
      3. **Images**: `docker save todo-chatbot-backend:$TAG -o /tmp/be.tar && mkdir -p /tmp/be && tar -xf /tmp/be.tar -C /tmp/be`, then `grep -rlIE '<patterns>' /tmp/be`; same for the frontend. **🔴 Check the layer format before trusting a clean result**: `grep` finds plaintext inside the uncompressed `layer.tar` files this normally produces, but if the layers come out **gzipped** (OCI layout) a plain `grep` reports *clean* on a compressed blob — a **false negative**. If so, decompress first: `find /tmp/be -name '*.tar.gz' -exec sh -c 'tar -xzOf "$1" | grep -aIE "<patterns>" && echo "HIT $1"' _ {} \;`. Record which form actually applied.
      4. **The direct check the owner asked for**: confirm **no `.env` file is inside either image** — `docker run --rm --entrypoint sh <img> -c 'ls -a / | grep -c "^\.env"'` returns `0` (and the same for the app directory) — and that `git status --porcelain` shows **no secret-bearing file tracked**.
      **Done when**: steps 1–3 report **0 findings in all three scopes** (or every finding is explained and fixed), step 4's `.env` count is `0` for both images, `git status` shows nothing secret tracked, and the exact commands that were run are written into the README (T058). **The image scans are the ones that actually test T013.**

- [ ] T065 🔁 **Clean-state acceptance run — one run from `minikube delete`** — satisfies **SC-005 (see waiver)**, FR-022, SC-001
      **Clean state is precisely defined** (spec Clarifications, 2026-09-15): the host has the toolchain available (re-installing is a no-op), `minikube delete` then `minikube start` has produced a **freshly created** cluster, any addon the procedure requires was enabled **by the procedure itself rather than assumed**, and **no release for this application is installed**. It does **not** mean a machine lacking the toolchain — that is SC-001's clean-*machine* claim, verified separately and once per FR-022.
      **Sequence**: `minikube delete` → `minikube start --driver=docker --cpus=4 --memory=4096 --ports=...` (exactly T033's command) → follow `README.md` **top to bottom** → run the acceptance sweep (T035–T056).
      **⚠️ Scope waiver — state it, do not paper over it.** SC-005 as written requires the procedure to pass **twice consecutively**. This revision runs it **once**, and there is **no database reset script** (T010 was dropped). T067 must report SC-005 as **partially satisfied / waived**, not as passed.
      **Done when**: every acceptance row passes, the wall-clock time is **under 60 minutes including toolchain installation**, and **zero steps were performed that are not in the README**. Every deviation found is a README defect — fix it, and record it, rather than working around it silently.

- [ ] T067 Sweep the spec's Acceptance Checklist and produce the completion report — satisfies constitution VII, SC-011
      **Done when**: every checkbox in spec.md's Acceptance Checklist is marked with a **captured command and its output** as evidence. **A step that was only reasoned about is not reported as verified** — that is the constitution's rule and it is what distinguishes this from a claim. The report MUST also carry an explicit **waived / not-verified / deviated** section listing **FR-020** (deviated by owner decision — the deployment targets `main`, not a dedicated branch), FR-018, FR-023, FR-028 and SC-005's second run, per the scope revision table at the top of this document — so the checklist is not overstated. **FR-020 is the one entry that is a conscious deviation rather than a scope cut**; report it as such, with the reason, rather than folding it in with the drops.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies. **Nothing in Phase 1 gates later work** — Q1, Q2 and Q3 are all closed, including T009's database choice (the existing database on `main`). **Phase 1 gates nothing.**
- **Foundational (Phase 2)**: depends on Setup. **Blocks all four user stories.** In particular **T013 must precede T031**, or a secret is baked into an image layer.
- **US1 (Phase 3), P1 🎯 MVP**: depends on Foundational. No dependency on US2–US4.
- **US2 (Phase 4), P2**: depends on Foundational (probes in T019/T020) and on US1 for a running application to kill.
- **US3 (Phase 5), P3**: depends on US1 (needs a deployed, working chatbot to scale).
- **US4 (Phase 6), P4**: depends on US1; T053 depends on T030.
- **Polish (Phase 7)**: **T064 → T065 → T067 are strictly sequential** (scan before the clean run; the sweep reports on the run). **T058 must be re-verified after T065.**

### Critical path

```
T009 (database) → T011–T013 (frontend packaging) → T014–T027 (chart)
   → T030 (procedure) → T031–T033 (build/load/cluster) → T034–T041 (MVP proof)
   → T042–T049 (US2/US3) → T050–T056 (US4) → T058 → T064 → T065 → T067
```

### Within each phase

- Contracts and configuration before chart templates (T006–T008 before T018–T020), because the templates consume those key names.
- Chart skeleton and values before Deployments (T014–T016 before T019–T020).
- Both source changes (T024, T025) before the frontend image is built (T031), or sign-in fails.
- Build before load before install (T031 → T032 → T035).
- Verification tasks prove the story; do not mark a story complete on the strength of "the earlier task passed".

### Parallel Opportunities

- **T001–T003** and **T006–T008** touch different files and can run together.
- **T012, T013, T014, T016, T017, T018, T021, T022, T023, T026** are independent files — one wave.
- **T019 and T020** are the two Deployments; independent files, but both depend on T015's values schema, so they follow it. They can run in parallel with each other.
- **T007 and T008** are independent of each other (different files verified, different contract sections).
- **T050–T052** (status, logs, resources) are three independent read-only verifications — one wave.
- **T058 and T063** are independent documents — one wave.
- **US2, US3, US4 verification waves** are independent of each other once US1 is green, if staffed — but they all mutate cluster state, so serialize them on a single cluster.

---

## Flagged Ambiguities

Per the instruction to flag rather than guess. **Three tasks carry a decision the plan did not make.**
None of them blocks a phase gate, and **T009 is no longer among them** — the owner resolved it on
2026-10-01 (see the Closed-since table below).

| Task | Flag | What is unresolved | Gates |
|---|---|---|---|
| **T002 (residue)** | ⚠️ NEW DECISION REQUIRED — surfaced while fixing T002 | The `specs/` half of the root mismatch is **fixed and verified**. Two other consumers of the same `$REPO_ROOT` still point at the parent repo: **`setup-plan.sh`'s template lookup** and **`create-phr.sh`'s template lookup *and* output directory**. Effect if left: `/sp.plan` warns and `touch`es an empty `plan.md` instead of copying the template, and script-created PHRs land in `Q4-Hackathon-2/history/prompts/` instead of this phase's — where FR-024/SC-011 evidence is expected. **Not fixed** — a `.specify/` and/or `history/` junction would have global reach and needs an owner call. | `/sp.plan`, `/sp.phr`, FR-024, SC-011 |
| **T033** | ⚠️ AMBIGUOUS | Whether `minikube start --ports` is supported by the docker driver on this host — **the one structural assumption the planning session could not confirm**. Fallback exists and is cheap, but it introduces a host-side long-running process the spec's edge case anticipated. | T035 → everything downstream |
| **T025** | ⚠️ AMBIGUOUS (low) | K2 (`useSecureCookies`) may turn out unnecessary — the plan keeps it because a silent cookie failure is expensive to diagnose. Revert path recorded in-task. | T036 |

**Closed since the plan was written** (no longer ambiguous — resolved by re-verification or owner decision):

| Item | Resolution |
|---|---|
| **T002 — the `specs/` half of the toolchain mismatch** | ✅ **RESOLVED and VERIFIED 2026-09-24, re-confirmed 2026-10-01.** A directory junction `Q4-Hackathon-2/specs/004-local-kubernetes-deployment` → this phase's real feature directory; `LinkType = Junction`, target intact. Deliberately **not** a link of `specs/` wholesale: this phase's `specs/` holds copies of `001-*`/`003-*`, which would let a `003-*` branch run silently read *this* phase's tree. Root `.gitignore` gained `/specs/` so the junction can never be committed. **Measured caveat**: because all four phases share one repo and one branch, phases 2's and 3's copies of the scripts also now exit 0 while on branch 004, resolving to this phase's `FEATURE_DIR`; on any other branch they fail loudly as before. See T002. |
| Plan **Q1** — how the Neon database is reached | ✅ **OWNER-DECIDED 2026-10-01: the Neon MCP server**, and the database is the **existing one on the `main` branch** — no `phase-iv` branch is created and nothing is provisioned. Supersedes the plan's `neonctl` / console / REST candidates; `neonctl` is confirmed absent and is **not** to be installed. **⚠️ This is a deliberate deviation from FR-020** ("a separate database or branch dedicated to this phase"): `main` is the branch Phase III uses, so browser activity during T036–T049 writes to live Phase III rows and both deployments share one JWT keypair. **T067 must report FR-020 as NOT SATISFIED.** The trade-off is accepted for a hackathon-scale demo with a handful of test users and no production load. This also **supersedes the earlier "phase-iv branch only — never touch main" constraint**, which existed solely to scope a purge that this revision withdrew. See T009. |
| Plan **Q2** — the Neon connection limit | ✅ **OWNER-ANSWERED 2026-10-01: 901**, read as `SHOW max_connections` on the compute's **direct** endpoint in the SQL Editor. It **is** the direct limit — there is no pooled/direct distinction to check. It is also **not** the basis of the stated replica maximum: that is the Minikube node's allocation (T041), with `8·B + 10·F ≤ 901` (`B ≤ 111` at `F=1`) kept as a non-binding footnote. An earlier draft of this document derived the maximum from this number against a different endpoint; that derivation is **wrong and withdrawn**, and its arithmetic is deliberately not restated here so no later reader can lift a stale figure out of context. |
| Plan **Q3** — which credential scanner proves SC-004 | ✅ **OWNER-ANSWERED 2026-10-01: none — no new tool is installed.** Supersedes both the plan's open candidate list and the earlier draft of this document, which had selected **TruffleHog** and made installing it a procedure step. TruffleHog, gitleaks and `docker scout` are all **rejected**; SC-004 is proven with `git grep` / `git log -p` / `docker save` + `grep`, all already present. See T064. |
| Plan **Q10** — Bash vs. PowerShell for `deploy/` | ✅ **OWNER-ANSWERED 2026-10-01: Bash.** The scripts run from Git Bash on this Windows host; PowerShell is not used. See T030. |
| Plan **Q7** — sanitize vs. sanitize-and-rotate for `.env.example` | ✅ **OWNER-ANSWERED 2026-10-01: sanitize to placeholders.** Rotation is not required by the task. **Measured finding that lowers the stakes**: `backend-api/.env.example` is **untracked and gitignored** (`backend-api/.gitignore:15`, confirmed with `git ls-files`), so those values were never committed. See T005. |
| **T009/T010's purge design** (8 tables in T009, 7 in T010, the `jwks` timing, the `neon.branch_id` guard) | ⛔ **SUPERSEDED 2026-10-01 — the entire purge/reset design is withdrawn.** The owner's instruction is **"no purge or reset script"**; T010 is dropped and T009 no longer purges. This overrides the earlier "OWNER-APPROVED … do not revisit" entry, which applied to a revision in which a reset script existed. **Consequence, now settled by T009**: the deployment targets **`main`**, which holds those 104 rows and its JWT keypair — so the Phase III and Phase IV deployments share **one dataset and one signing key**. That is the accepted trade-off, not a defect to fix. |
| Plan D5's "zero rows of Phase III production data" on the parent | ❌ **FALSIFIED by measurement (2026-09-24).** `main` holds **104 rows** across 8 tables, spanning 2026-01-14 → 2026-03-29. With the purge withdrawn, this is now a **known property of the environment** rather than a defect to remediate. |
| Frontend direct database access | ✅ **CONFIRMED** against Phase III source — `frontend/lib/auth-server.ts:6-11`. No owner decision needed. See T008. |
| Second exposed backend port (FR-005) | ✅ **CONFIRMED** against Phase III source — `frontend/lib/api-client.ts:31`, sole importer `frontend/app/(protected)/tasks/[id]/edit/page.tsx:5`. No owner decision needed. See T007. |

### Neon MCP tool contracts — reference only

**⚠️ Read this first:** the owner's decision on 2026-10-01 (T009) is to use the **existing database on
`main`**. That leaves **one** tool in actual use — `get_connection_string` — and it is **read-only**. Every
other row below is retained as a **rejected-alternative reference**, so the decision is not re-litigated
and the path back is documented if the FR-020 deviation is ever reversed. **No `destructiveHint: true`
tool is used anywhere in this feature.**

Tool names and signatures were read from the live server's unauthenticated tool listing
(`https://mcp.neon.tech/api/list-tools?category=branches`), not from documentation prose.

| Tool | Key parameters | Confirmed behaviour / constraint | Status |
|---|---|---|---|
| `get_connection_string` | `project_id` (req), `branch_id`, `database_name`, `role_name` | Returns the `DATABASE_URL`. Write-access only. | ✅ **THE ONLY ONE USED** — T009 step 1, to confirm the Secret's value resolves to `br-snowy-surf-ahjdfzub`. |
| `get_default_branch` | `project_id` | Resolves the parent id. Do not hardcode `br-...`. | ⛔ Not needed — no branch is created. |
| `create_branch` | `project_id` (req), `name`, `parent_id`, `compute{...}`, `no_compute` | "Creates a branch with a read-write compute and waits until it is ready… Copies the parent at HEAD." **Does not return a connection string.** | ⛔ Not needed — would have created the withdrawn `phase-iv` branch. |
| `get_branch` / `list_branches` | `project_id`, `branch_id` | Name→id resolution; `expires_at` readback. | 🔍 Useful only to **assert `main` is `ready`** (T009 step 2), since `main` was once observed `archived`. |
| `update_branch` | `project_id`, `branch_id`, `name`, `protected`, `expires_at` | Sets `expires_at: null` — the former TTL fix. | ⛔ Not needed — it existed for the created branch's TTL, which no longer applies. |
| `describe_branch` | `project_id`, `branch_id` | Tree view of databases, schemas, tables. | ➖ Optional, read-only. |
| `reset_from_parent` | `project_id` (req), `branch_id` (req, **id not name**), `preserve_under_name` | **⛔ NOT USED.** Semantics: "Reset a branch to its parent's current HEAD." That would re-import the parent's rows, and it is marked `destructiveHint: true` with *"NEVER run autonomously"*. Recorded so the rejection is not re-litigated. | ⛔ **Never.** Out of scope entirely. |

**Server configuration**: `https://mcp.neon.tech/mcp`, **write mode active** (`readOnly: false`). Because
T009 no longer writes, the destructive-tool notice the server itself emits — *"For tools with
`destructiveHint: true`, NEVER invoke autonomously; always ask the user first"* — **now applies to nothing
in this feature.** If a future revision reverses the FR-020 deviation and provisions a branch, it applies
again immediately.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup — **only T009's database choice blocks anything.** Resolve it, then the workstream is clear.
2. Phase 2 Foundational — **T013 before T031**, always.
3. Phase 3 US1 — the whole documented procedure, then T035–T041.
4. **STOP and VALIDATE**: the application is running on the cluster and browser-reachable. This alone satisfies the spec's headline acceptance criteria and SC-001.
5. **This is genuinely shippable.** Phases 4–6 are verification of properties the Deployment controller and the Phase III architecture already provide.

### Incremental Delivery

1. Setup + Foundational → the chart renders, images build, the database is pointed at.
2. **US1** → the MVP. The application runs on the cluster and is browser-reachable. **Deploy/demo.**
3. **US2** → proven self-healing. Adds operational confidence, no new artifacts.
4. **US3** → proven scalability. Adds the strongest evidence that Phase III's statelessness holds.
5. **US4** → proven operability and update path.
6. Polish → the README is proven by T065, not merely written; SC-004 is proven by T064.

### Note on the shape of this task list

This is a **deployment and operations** feature. Three of the seven phases (US2–US4) are **verification
tasks**, because the artifacts those stories need — probes, resource boundaries, replica counts, graceful
shutdown — are declarative and land in the Foundational phase. The spec's Success Criteria are almost all
*observable outcomes* (recovery within 2 minutes, exactly-once application, zero duplicates), and
constitution VII requires each to be backed by a captured command rather than asserted.

---

## Notes

- **[P] tasks** touch different files and have no dependency on incomplete tasks.
- **[Story] labels** map every user-story task to its spec.md story, for traceability (constitution VIII).
- **Commit after each task or logical group**; every commit message should name the `FR-###`/`SC-###` it advances.
- **Never hand-edit a deployed resource to correct the browser-facing address** — the spec forbids it, and the address is a build-time constant (T034 catches the stale-build case).
- **Do not add a metrics addon.** SC-010 is satisfied by declared resource boundaries read back from the cluster (T052), not by consumption metrics.
- **Do not install `kubectl-ai`, `kagent`, `neonctl`, TruffleHog, or any other tool.** FR-026 and the scope revision both forbid resting an acceptance criterion on a new install (T063, T064).
- **Every AI-assisted operation gets a `history/` record naming the assistant** (T063, SC-011) — Gordon included, and every substitution recorded.
