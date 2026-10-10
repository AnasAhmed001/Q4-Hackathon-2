# Environment Contract — per-service variable matrix

**Feature**: `004-local-kubernetes-deployment`
**Tasks**: T006, T007, T008 — satisfies FR-005, FR-007, FR-008, and **FR-020's direct-access clause only**
**Created**: 2026-10-01

This is the single matrix both services' configuration is built from. Every variable the two workloads
consume appears here exactly once, with its **consumer**, its **source**, and its **Phase IV value**.

> **Read the scope note on FR-020 before treating this file as "FR-020 satisfied".** §4 records the
> *direct-access* clause as CONFIRMED, and it is. The *dedicated-branch* clause is **deviated** by owner
> decision — see T009 and `research.md` §3. A green tick here does not mean FR-020 passes overall.

---

## 1. The matrix

**Consumer** is the load-bearing column. Three distinct consumers exist, and a value placed for one is
ignored by the others:

- **frontend-build** — inlined into the browser bundle by `next build`. Supplied as a Docker
  `--build-arg`. Changing it requires **rebuilding the frontend image**.
- **frontend-runtime** — read by the Next.js server process at request time. Supplied by ConfigMap /
  Secret.
- **backend-runtime** — read by the FastAPI process at startup. Supplied by ConfigMap / Secret.

| Variable | Consumer | Source | Phase IV value |
|---|---|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | frontend-**build** | Docker `--build-arg` | `http://localhost:30800` |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | frontend-**build** | Docker `--build-arg` | `http://localhost:30080` |
| `BETTER_AUTH_URL` | frontend-runtime | ConfigMap | `http://localhost:30080` |
| `BETTER_AUTH_JWKS_URL` | backend-runtime | ConfigMap | `http://todo-chatbot-frontend:3000/api/auth/jwks` |
| `ALLOWED_ORIGINS` | backend-runtime **and** frontend-runtime | ConfigMap | `http://localhost:30080` |
| `BETTER_AUTH_SECURE_COOKIES` | frontend-runtime | ConfigMap | `false` |
| `NODE_ENV` | frontend-runtime | ConfigMap | `production` |
| `DATABASE_URL` | **both** services, runtime | **Secret** | Neon `main` pooled URL — see §4 |
| `BETTER_AUTH_SECRET` | frontend-runtime | **Secret** | from `deploy/.env.deploy` |
| `GEMINI_API_KEY` | backend-runtime | **Secret** | from `deploy/.env.deploy` |
| `ENVIRONMENT` | backend-runtime | ConfigMap | `production` |
| `LOG_LEVEL` | backend-runtime | ConfigMap | `info` |
| `PYTHONDONTWRITEBYTECODE` | backend-runtime | Deployment `env` | `1` — see §5 |

---

## 2. The `BETTER_AUTH_URL` trap (D6) — the entry that breaks every request if missed

**The backend calls the frontend.** `backend-api/src/auth/jwt_validator.py:49-59` fetches the Better Auth
JWKS endpoint at `BETTER_AUTH_URL + /api/auth/jwks`. In-cluster, that must be the frontend **Service DNS
name**, not the browser-facing URL.

So one variable name needs **two different values depending on which pod consumes it**:

| | Value | Why |
|---|---|---|
| Frontend consumes `BETTER_AUTH_URL` | `http://localhost:30080` | Better Auth's server `baseURL`. Must equal the **browser-facing origin**, or generated URLs and cookie scoping break. |
| Backend needs the JWKS location | `http://todo-chatbot-frontend:3000/api/auth/jwks` | Fetched **over the pod network**. |

**🔴 Pointing the backend at `localhost:30080` would make the pod fetch JWKS from *itself*** — there is
no Better Auth server in the backend container — and **every authenticated request would 401**.

**Resolution**: the dedicated `BETTER_AUTH_JWKS_URL` override, which takes **priority** at
`jwt_validator.py:51`. Setting it leaves `BETTER_AUTH_URL` unambiguous for the frontend. Both keys are in
the ConfigMap (§1); the backend reads the JWKS one only.

---

## 3. `NEXT_PUBLIC_*` values are build-time and deliberately absent from the ConfigMap

The two `NEXT_PUBLIC_*` entries in §1 are **build** values. They are **deliberately not present in the
runtime ConfigMap**, because placing them there would be actively misleading: `next build` has already
inlined them into the browser bundle, and the running container ignores them entirely.

**Consequence, stated loudly (spec edge case, D3)**: changing a declared port requires a **frontend image
rebuild**. The ConfigMap cannot correct it at runtime. T034 is the check that catches a stale build.

---

## 4. Verification records

### 4.1 FR-005 — the one client-side direct backend call ✅ CONFIRMED (T007)

**Verdict: CONFIRMED against Phase III source.**

| Element | Evidence |
|---|---|
| The call site | `frontend/lib/api-client.ts:31` — `const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL \|\| 'http://localhost:8000';` |
| Its **sole** importer | `frontend/app/(protected)/tasks/[id]/edit/page.tsx:5` — a `'use client'` component |

Because the importer is a client component, this call runs **in the browser** and needs a
**host-reachable** backend address. **No second path exists** — this is the entirety of FR-005, and it is
exactly the "one client-side call path" of spec Risk #2.

**⚠️ Hazard found during verification, sharper than the plan recorded.** The fallback at
`api-client.ts:31` is **`http://localhost:8000`**, but the backend container listens on **7860**
(`backend-api/Dockerfile`, `CMD uvicorn ... --port 7860`). If `NEXT_PUBLIC_BACKEND_URL` is **not** baked
at build time, this page silently calls a **dead port** — a failure that looks like an application bug.
Mitigated by T034's post-build proof, and verified explicitly by T037.

### 4.2 Frontend direct database access ✅ CONFIRMED (T008)

**Scope: FR-020's *direct-access* clause only. Its *dedicated-branch* clause is deviated — see T009.**

| Element | Evidence |
|---|---|
| The connection | `frontend/lib/auth-server.ts:6-11` — `const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized: false } })` |
| Its use | passed as `database: pool` at `auth-server.ts:15`. Better Auth's `user`/`session`/`account`/`jwks` tables live in Postgres. |

**Therefore `DATABASE_URL` is a frontend *runtime* Secret key, not backend-only.** It appears once in §1
and is mounted into **both** Deployments.

**One URL serves both services** — the two consumers differ in how they treat it:

| Service | Treatment |
|---|---|
| **Backend** | `settings.py:33-49` rewrites `postgresql://` → `postgresql+asyncpg://` and `sslmode=require` → `ssl=require` |
| **Frontend** | `pg.Pool` consumes it **as-is**, with `rejectUnauthorized: false` |

The **pooled** (`-pooler`) endpoint is therefore correct for both, and matches the shape Phase III
already uses.

### 4.3 FR-008 — credentials are replaceable without a rebuild ✅ BY CONSTRUCTION

Every credential in §1 is a **runtime** env value delivered by `secretKeyRef`, never a build arg. No
image embeds one, so re-creating the Secret and running `kubectl rollout restart deploy` brings both
workloads onto a new value **with no image rebuilt**. Confirmed by T055.

### 4.4 FR-007 — nothing sensitive in images, git, or logs

- Credentials exist only in the Secret, materialized from the gitignored `deploy/.env.deploy` (T026,
  T027) — never in `values.yaml`, which references the Secret **by name** (`existingSecret`).
- Both images are built with a `.dockerignore` that excludes `.env*` (T013 — security-critical, and
  **must land before T031** or `frontend/.env` bakes into a layer).
- Nothing in §1 is logged by either service.

---

## 5. Read-only-rootfs implications (D7)

Both containers run with `readOnlyRootFilesystem: true`, which is why §1 carries one entry that is not
really "configuration":

- `PYTHONDONTWRITEBYTECODE=1` — the backend would otherwise try to write `__pycache__` into the
  read-only layer on first import and fail.
- The backend additionally gets an `emptyDir` at `/tmp`; the frontend gets one at `/app/.next/cache`
  (without it Next.js fails on its first cache write).

Both are declared in the Deployments (T019, T020), not here — recorded so the reason is not lost.
