# Research — Phase IV Local Kubernetes Deployment

**Feature**: `004-local-kubernetes-deployment`
**Created**: 2026-10-01
**Task**: T001 (toolchain baseline), T004 (plan open questions Q1–Q10)

This document records **measured facts and closed decisions**. Where a value was observed by running
a command, the command is shown. Nothing here is inferred from documentation prose.

---

## 1. Toolchain baseline (T001 — satisfies FR-021, FR-022, SC-001)

Observed on this host (Windows 10 Pro 19045, Git Bash) on 2026-10-01:

| Tool | Present | Version | Command used | Notes |
|---|---|---|---|---|
| `docker` | ✅ | `29.1.3` (build `f52814d`) | `docker --version` | Client present. **Daemon was initially down**; brought up via Docker Desktop before any build. |
| `docker ai` (Gordon) | ✅ | plugin present | `docker ai --help` | Rejects `--version` but parses subcommands. Used for build assistance (FR-025). |
| `kubectl` | ✅ | Client `v1.34.1` | `kubectl version --client` | |
| `minikube` | ❌ → installing | — | `minikube version` → `command not found` | **Absent at baseline.** Its absence is exactly what makes installing it a *procedure step* (FR-021) rather than a prerequisite. |
| `helm` | ❌ → installing | — | `helm version` → `command not found` | **Absent at baseline.** Same reasoning as `minikube`. |
| `neonctl` | ❌ | — | — | **Deliberately not tracked and NOT to be installed.** The database is reached through the Neon MCP server (Q1, T009). |

**Package managers available for the install step**: `winget v1.29.380`, `choco 2.6.0`.
`scoop` is absent.

**Install commands adopted by the procedure** (verified to run on this host):

```bash
winget install --id Kubernetes.minikube --accept-source-agreements --accept-package-agreements
winget install --id Helm.Helm           --accept-source-agreements --accept-package-agreements
```

**Consequence for SC-001**: because both tools are absent on a genuinely clean machine, the 60-minute
budget *includes* installing them. This is the FR-021/FR-022 position, and it is stated in the README.

---

## 2. Closed decisions (T004 — plan Q1–Q10)

### Q1 — How is the Neon database reached? ✅ RESOLVED (owner, 2026-10-01)

**Through the Neon MCP server** — never `neonctl`, never the console, never the REST API. `neonctl` is
confirmed absent and is **not** to be installed.

**And the database is the existing one on the `main` branch** — no `phase-iv` branch is created, and
nothing is provisioned. See §3 below, which records the resulting FR-020 deviation.

The tool names and signatures in the task list were read from the live server's tool listing
(`https://mcp.neon.tech/api/list-tools?category=branches`), not from documentation prose.

### Q2 — What is the Neon connection limit? ✅ RESOLVED (owner, 2026-10-01)

**901.** Read as `SHOW max_connections` on the compute's **direct** Postgres endpoint in the Neon SQL
Editor. It **is** the direct limit — there is no separate pooled-vs-direct number to contrast, and it is
not a pooled-only figure.

**It is not the basis of the stated replica maximum.** That is derived from the Minikube node's
allocation (T041), because scheduling is governed by *requests* against *node allocatable*, and the node
is the binding constraint on a laptop. The connection budget `8·B + 10·F ≤ 901` is retained as a
**secondary, non-binding footnote** (`B ≤ 111` at `F = 1`).

> **Note on drift from plan.md**: `plan.md` still shows Q2 as open and contains an earlier derivation of
> the replica maximum from this number against a different endpoint. That derivation is **wrong and
> withdrawn**. `plan.md` is the planning session's frozen record; this document and `tasks.md`
> supersede it.

### Q3 — Which credential scanner proves SC-004? ✅ RESOLVED (owner, 2026-10-01)

**None — no new tool is installed.** SC-004 is proven with tools already present on any machine running
the procedure: `git grep` / `git log -p` for tracked files and history, and `docker save` + `grep` for
the two built images.

**Rejected**: TruffleHog (the earlier draft selected it and made installing it a procedure step),
gitleaks (repository-only), `docker scout` (reports CVEs, not credentials). See T064.

### Q4 — Are the four source changes acceptable? ✅ ACCEPTED (option A)

All four are accepted: `frontend/next.config.ts` (`output: 'standalone'`), `frontend/lib/auth-server.ts`
×2 (`trustedOrigins`, `useSecureCookies`), plus two new frontend packaging files (`Dockerfile`,
`.dockerignore`). Each is forced by an explicit requirement — K1 by FR-007, K2 by User Story 1, the
packaging files by FR-001/FR-017 — not by preference.

Option B (pin the frontend NodePort to `3000` so the hardcoded origin still matches) is **rejected**:
it works *around* FR-007's "must not be embedded in the repository" rather than meeting it, and it
couples the cluster to a non-default port range. See K1 in `plan.md`.

### Q5 — Which Minikube driver is authoritative? ✅ DOCKER

`--driver=docker`. Docker Desktop 29.1.3 is present on this host, and `--ports` (the chosen exposure
mechanism) is a docker/podman-driver feature only.

### Q6 — Is `minikube start --ports` acceptable as primary? ✅ YES, with an unverified caveat

Option (a): `--ports` is **primary**, with `kubectl port-forward` as the documented fallback. This is a
pinned, predictable `http://localhost` address with no hosts-file entry and no extra long-running host
process.

**✅ VERIFIED AT T033 (2026-10-01) — `--ports` works on the docker driver on this host.** The
assumption the planning session could not confirm by documentation lookup is now a measured fact:

```
$ docker inspect minikube --format '{{json .NetworkSettings.Ports}}'
"30080/tcp": [{"HostIp":"0.0.0.0","HostPort":"30080"}, {"HostIp":"::","HostPort":"30080"}]
"30800/tcp": [{"HostIp":"0.0.0.0","HostPort":"30800"}, {"HostIp":"::","HostPort":"30800"}]
```

Both pinned NodePorts are published to the host at the **same numbers**, on IPv4 and IPv6. `minikube
start` accepted the flag with no `MK_USAGE` or unsupported-driver error.

**Consequence**: the `kubectl port-forward` fallback is **not** adopted as primary and **no host-side
long-running process is required**. It is retained in the README as the documented recovery path, since
some Docker Desktop / WSL configurations forward published container ports differently — but the
host-process dependency the spec's edge case anticipated **does not apply here**.

### Q7 — Sanitize `backend-api/.env.example` and rotate? ✅ SANITIZE ONLY

Sanitize to placeholders. Rotation is **not** required by any task.

**Measured finding that lowers the stakes**: `backend-api/.env.example` is **untracked and gitignored**
— `git check-ignore -v` reports `backend-api/.gitignore:15:.env.example`, and `git ls-files` confirms it
is not in the index. Those values were therefore **never committed and are not in git history**. T064's
history scan is the check that proves it.

### Q8 — Frontend health probe shape? ✅ OPTION (a) — no new source file

Readiness `httpGet /login`, liveness `tcpSocket :3000`, startup `httpGet /login` 30 × 2s. No
`app/api/health/route.ts` is added. `/login` is public, unauthenticated, and renders a real page without
touching the database — which is the property SC-007 wants.

### Q9 — Should the frontend `pg` pool be lowered? ✅ OPTION (a) — leave the default

`pg-pool`'s default `max: 10` is left as-is; **no source change**. The connection budget is a footnote
(Q2), not the binding constraint, so spending a fifth source change to shave a non-binding number is not
justified. Each frontend replica is *stated* alongside the backend count (10 connections ≈ 1.25 backend
replicas) rather than silently folded in.

### Q10 — Bash or PowerShell for `deploy/`? ✅ BASH (owner, 2026-10-01)

The scripts are **Bash**, run from Git Bash on this Windows host. PowerShell is not used. The form is
kept consistent across `deploy/deploy.sh`, the helper commands, and the README.

---

## 3. Database decision and the FR-020 deviation (T009)

**Decision (owner, 2026-10-01): "use the same branch which is the main branch."**

- **Project**: `billowing-wind-59531724`
- **Branch**: `main` = `br-snowy-surf-ahjdfzub`
- No `phase-iv` branch is created. Nothing is provisioned. **No MCP write is performed by this task.**

### 🔴 This is a recorded deviation from FR-020 — not a compliant choice, and not a silent one

FR-020 requires Phase IV to target *"a separate database or branch dedicated to this phase, so that
verification runs are repeatable and non-destructive against Phase III data."* **`main` is not that.**

Both halves of FR-020's stated rationale fail together:

- The deployment reads and writes **the same database the Phase III deployment uses**, which holds
  **104 rows** across 8 tables (`message` 64, `conversation` 17, `task` 9, `session` 5, `account` 4,
  `user` 4, `jwks` 1 — measured 2026-09-24).
- **Browser activity during T036–T049 writes into that live data.** Signing in, sending chat messages
  and creating tasks all mutate Phase III's rows. Treat the demo as operating on the real system,
  because it is.
- Both deployments share **one JWT keypair** in `jwks`, so a token minted by either deployment
  validates against the other.
- Verification is therefore **not** "repeatable and non-destructive against Phase III data".

**Accepted trade-off, given the context**: a hackathon learning project with a handful of test users, no
production-scale load, and no purge or reset to run. The deviation removes an entire provisioning step.

**T067 MUST report FR-020 as NOT SATISFIED**, with this reason — not as passed, and not folded in with
the dropped-task waivers.

### What T009 actually does (read-only)

1. Resolve the `DATABASE_URL` for `main` via the Neon MCP `get_connection_string`, to **confirm the
   Secret's value is the intended one** — not to discover it. The owner already holds it in
   `backend-api/.env` and `frontend/.env`.
2. **Assert the branch is `ready` before relying on it.** `main` was once observed `archived` and had
   to be woken. A sleeping branch surfaces as a connection failure at T035, not as an obvious
   "wake me" error, so this is checked here rather than debugged later.

### Superseded history

This section **supersedes** the earlier "phase-iv branch only — never touch main" constraint. That
constraint was written for a **purge** operation in the old T009/T010 design, which this revision
withdrew in full. There is no purge and no reset script, so it no longer describes anything that
exists. Read it as history, not as a live rule.

### Neon MCP tools — status

| Tool | Status |
|---|---|
| `get_connection_string` | ✅ **the only one used** (step 1) |
| `get_branch` / `list_branches` | 🔍 used only to assert `main` is `ready` (step 2) |
| `create_branch`, `get_default_branch`, `update_branch` | ⛔ moot — they existed solely for the withdrawn `phase-iv` branch |
| `reset_from_parent` | ⛔ **never** — `destructiveHint: true`, and it would reset to the parent's HEAD |

**No `destructiveHint: true` tool is used anywhere in this feature.**

---

## 4. Backend image dependencies — `requirements.txt` is unsatisfiable (T031)

Found when the first `docker build` of the backend failed. The plan's assumption
that `backend-api/Dockerfile` could be reused **as-is** was wrong; this records
what was done instead.

### The finding

`backend-api/requirements.txt` cannot be installed by any pip resolver:

- `fastapi==0.104.1` declares `anyio<4.0.0,>=3.7.1`
- `mcp==1.26.0` declares `anyio>=4.5` — and also `httpx>=0.27.1`, `pydantic>=2.11.0`, `uvicorn>=0.31.1`
- `requirements.txt` pins `mcp==1.0.0`, `httpx==0.25.2`, `pydantic==2.5.0`, `uvicorn==0.24.0`

→ `ResolutionImpossible`.

The `mcp==1.0.0` pin is wrong on its own terms: `backend-api/src/mcp/server.py:9`
does `from mcp.server import FastMCP`, which 1.0.0 does not export. The pin is
stale, not a requirement.

### No authoritative lock exists

| Candidate | Verdict |
|---|---|
| `poetry.lock` / `uv.lock` | ❌ do not exist |
| `pyproject.toml` | ❌ stale — caret ranges exclude the running versions (`httpx ^0.25.0` vs installed 0.28.1; `openai-agents ^0.1.0` vs 0.8.0; `litellm ^0.50.0` vs 1.81.8; `bcrypt ^4.0.1` vs 5.0.0) |
| `backend-api/.venv` | ✅ **the only working environment** |

The venv carries `anyio 4.12.1` **in violation of `fastapi 0.104.1`'s own
metadata**. It therefore was not produced by a strict resolver and cannot be
re-derived by one either — which is why reproducing it, rather than re-resolving,
is the only faithful option.

### Decision

- **`backend-api/requirements.lock.txt`** — generated by `pip freeze` of the
  venv (86 packages; `pywin32` dropped as Windows-only). Its header records
  provenance and the reasoning.
- **`backend-api/Dockerfile`** installs it with `--no-deps`.

`--no-deps` is **required, not a shortcut**: because the fastapi/anyio conflict is
real, even a *resolving* install of the lock fails. The freeze is complete —
every transitive dependency is pinned — so skipping resolution reproduces the
proven set instead of substituting a different one.

### Explicitly NOT done

- Runtime versions were **not** modernized. Bumping `fastapi` to ≥0.115 would
  resolve cleanly but would deploy a stack Phase III was never tested on.
- `backend-api/requirements.txt` was **not** modified — it is shared with the live
  Phase III deployment.
- No application source was changed.

### Verified (2026-10-01)

| Check | Result |
|---|---|
| `docker build` | ✅ exit 0, image 538 MB |
| `import src.main` with env set | ✅ `IMPORT_OK` |
| Same, as UID 1000 + `--read-only` + tmpfs `/tmp` | ✅ `IMPORT_OK_NONROOT` |
| Uvicorn starts | ✅ `Uvicorn running on http://0.0.0.0:7860` |
| `GET /health` over a published port, DB unreachable | ✅ **HTTP 200 in ~6s** — the D8/SC-007 behavior |

> Incidental confirmation of FR-010: importing with **no** `DATABASE_URL` set
> fails immediately with `sqlalchemy.exc.ArgumentError: Could not parse
> SQLAlchemy URL from string ''`. Left unset, the app dies at import rather than
> starting half-configured — which is exactly why the Deployment uses
> `secretKeyRef` with `optional: false`.

---

## 5. Procedure defects found by actually running it (T030)

`deploy/deploy.sh` was written, reviewed, and then **run**. Three defects surfaced that reading it
did not reveal. Both are recorded because a clean-state run is the only thing that finds this class
of bug, and because T065 depends on the script being trustworthy.

### 5.1 `set -o pipefail` + `grep -c` = false "secret in image"

The post-build gate that checks for a baked `.env` was:

```bash
docker run --rm --entrypoint sh "$IMG" -c 'ls -a /app | grep -c "^\.env"' | grep -qx 0 \
  || die "secret-in-image: …"
```

`grep -c` **exits 1 when it matches nothing** — it prints `0` *and* reports failure. Under
`set -o pipefail` (set at the top of the script) that status becomes the pipeline's, so `|| die`
fires on a **clean** image. Measured:

| Invocation | Result |
|---|---|
| `docker run … \| grep -c "^\.env"` | prints `0`, **exit 1** |
| Same pipeline, `pipefail` **off** | `OK` |
| Same pipeline, `pipefail` **on** (what the script runs) | `FAIL` |

The image was never dirty — `/app` contains only `.next`, `node_modules`, `package.json`, `public`,
`server.js`. **The gate was broken, not the image.**

**Fixed** by neutralising the exit code at source so the *count* decides — and extended to check
both `/` and `/app`, which is what T064 step 4 requires:

```bash
envcount=$(docker run --rm --entrypoint sh "$IMG" -c "ls -a ${dir} | grep -c '^\.env' || true")
[ "$envcount" = "0" ] || die "secret-in-image: …"
```

> **This is a false *positive*, which is the safe direction** — it aborts a good build rather than
> passing a bad one. Worth recording anyway, because a gate that cries wolf on a clean image is a
> gate someone eventually disables.

### 5.2 The Secret was created before the namespace existed

Step 6 created the Secret in `todo-chatbot`, but nothing created that namespace — step 7's
`helm upgrade --install --create-namespace` runs **later**. On a genuinely fresh cluster
(T065's defined starting state) this failed hard:

```
Error from server (NotFound): error when creating "STDIN": namespaces "todo-chatbot" not found
```

It did not appear on the earlier runs only because an earlier `helm` invocation had already
created the namespace — i.e. **the bug was invisible exactly until the clean-state run**, which is
the run that matters.

**Fixed** declaratively, so this remains an apply rather than a mutation (FR-003):

```bash
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
```

### 5.3 The backend build context

`deploy/deploy.sh` invoked `docker build … backend/`; the directory is `backend-api/`. Caught before
the first run.

### 5.4 The quoted `DATABASE_URL` reached the Secret

The first **successful** install brought the frontend up and put the backend in `CrashLoopBackOff`.
The log named the cause exactly:

```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string
  '"postgresql://neondb_owner:…@ep-falling-sea-…neon.tech/neondb?…"'
```

Those are **literal `"` characters inside the value**. `deploy/.env.deploy` had
`DATABASE_URL="postgres://…"`, and **`kubectl create secret --from-env-file` does not strip
surrounding quotes** the way Docker Compose does — so the quotes shipped into the Secret. Measured:
the stored value was **150 chars beginning and ending with `"`**; the real URL is **148**. The other
two keys were unquoted and correct.

Quoting is legitimate `.env` style, so the fix **normalizes rather than forbids**: `deploy.sh` now
strips an optional matching quote pair per line before building the Secret, and then asserts that
**no stored value begins with a quote character**. The assertion is the part that matters — it turns
a runtime crash into a build-time abort that names the key.

### 5.5 `mktemp` returns a path a native-Windows `kubectl` cannot read

Normalizing required a temp file. The first version used `tmpenv="$(mktemp)"`, which under Git Bash
returns `/tmp/tmp.Yu33RNfLDj`. `kubectl` is a **native Windows binary**, and with
`MSYS_NO_PATHCONV=1` (set earlier to stop Git Bash mangling `docker --tmpfs` paths) Git Bash does
**not** translate it:

| Path handed to kubectl | Result |
|---|---|
| `/tmp/tmp.Yu33RNfLDj` | ❌ `error reading …: The system cannot find the path specified` |
| `deploy/.env.deploy.normalized.$$` (relative) | ✅ resolves from the working directory |

**Fixed** by using a relative path, with `.gitignore` gaining
`deploy/.env.deploy.normalized*` so a killed run cannot leave a committable credential.

**Compounding defect**: the failing command had `2>/dev/null`, which discarded the precise
`cannot find the path specified` and left only the downstream, misleading
`error: no objects passed to apply`. **The `2>/dev/null` on that line is now removed**, so the real
error is the one that surfaces.

### 5.6 `--wait --timeout 5m` measures wall-clock, and CrashLoopBackOff backs off exponentially

After §5.4 was fixed, the next run still ended `UPGRADE FAILED: … status: Failed, message:
Progress deadline exceeded` — even though the pod was **healthy by the time it was read**:

```
todo-chatbot-backend-59476594c9-db97t   1/1   Running   9 (6m10s ago)   22m
todo-chatbot-frontend-875dfd748-wqbld   1/1   Running   0               22m
$ curl -o /dev/null -w '%{http_code}' localhost:30800/health   -> 200
$ curl -o /dev/null -w '%{http_code}' localhost:30080/login    -> 200
```

The two facts are consistent, and the reason matters. A `secretKeyRef` is resolved **at container
creation time**, not continuously — so the pod running from the old revision could not pick up the
corrected Secret until its **next restart**. It had already crashed 9 times on the quoted URL, so
the kubelet was in exponential backoff (10s → 20s → 40s → … → 300s). The corrected value arrived,
the *next* restart came up clean, and the app has been serving `/health` 200 ever since.

By then the Deployment had long since been marked `Failed` (progress deadline exceeded), so
`helm --wait` returned that verdict — **correctly**. This is not a defect in the chart or the
script:

- **`--wait` failing is the right behaviour.** It refused to report a release as deployed while a
  workload was not Ready. The alternative — reporting success on a crashlooping pod — is exactly
  what `--wait` exists to prevent.
- **It cannot occur on a clean run (T065).** The backoff was accumulated damage from the §5.4 bug.
  From an empty cluster the Secret is correct on first apply, the pod starts once, and `/health`
  answers in ~6s against a 300s budget.
- **Recovery is the ordinary path.** Helm 4 leaves the release recoverable and a re-run upgrades
  from it — exactly as `deploy.sh`'s own header claims ("running it twice installs fresh once and
  updates in place thereafter"), which is what that re-run then verified.

**Recorded because the failure mode is misleading**: "Progress deadline exceeded" reads like a
broken application, when the application was in fact healthy and only the *release record* was
stale. Note also that `helm list` shows `failed` while `kubectl get deploy` shows `1/1` — the two
are describing different things, and only the second is the application's current state.

### 5.7 curl exits 23 on a healthy response, so the reachability check false-alarmed

`deploy.sh` step 2 tested host reachability with curl's **exit status**:

```bash
if curl -sS -o /dev/null -m 5 "http://localhost:${FE_NP}/login" 2>/dev/null; then
```

Under Git Bash on this host, with `-o /dev/null`, curl returns **exit 23 (`CURLE_WRITE_ERROR`)
even on a clean HTTP 200**. Measured:

```
http://localhost:30800/health   http=200   curl_rc=23
http://localhost:30800/docs     http=404   curl_rc=23
http://localhost:30080/login    http=200   curl_rc=23
```

The status is 23 regardless of the response, so `if curl …` always takes the **else** branch and
the script warns `not reachable yet` **for a frontend that is serving 200s**. This was not
theoretical: two consecutive runs printed that warning while the app was verifiably up, which is
exactly how it was noticed — the warning contradicted a `curl` run moments earlier.

The cost is a **misleading diagnostic**, not a broken deployment: the step is advisory and the run
continued. But it points the reader at the port-forward fallback for a problem that does not exist,
and it undermines the recorded T033 branch — a reachability step that always says "unreachable"
cannot be the evidence that `--ports` works.

**Fixed** by testing the **HTTP code**, which is written to stdout regardless of the write error:
`fe_code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 … || true)` then comparing to `200`. The
`|| true` matters — the non-zero status would otherwise poison the pipeline under `set -e`. The
warning text now reports the code actually received rather than asserting a cause.

> Note this is the same family as §5.1: **a POSIX tool's exit status is not always the signal you
> want**, and `set -e`/`pipefail` turn that mismatch into a wrong branch rather than a visible
> error. Both were found by running the script, not by reading it.

### 5.8 Restart re-verification: what survived, and a `kubectl wait` trap

Two restarts were exercised on 2026-10-09, and both preserved the deployment entirely.

**(a) Docker Desktop restarted after 8 days down.** The cluster container read
`Exited (137) 8 days ago` — Docker Desktop's shutdown killed it, and it took the whole stack with
it: `docker info` failed, and helm/kubectl reported `cluster unreachable`. Nothing was lost:
`minikube start` resumed the **existing** profile in 2m27s, and afterwards

| Check | Result |
|---|---|
| `docker inspect minikube` ports | `30080/tcp` and `30800/tcp` still published to `0.0.0.0` |
| helm release | still `REVISION: 3`, `STATUS: deployed` — **not reinstalled** |
| pods | same pods, `AGE 8d`, containers restarted in place |
| reachability | `/login` 200, `/health` 200 |

**(b) T039's literal sequence — `minikube stop` then `minikube start`.** Same outcome: both
deployments `1/1 AVAILABLE`, both ports 200, helm still revision 3, **no build and no install** run.
This is exactly T039's done-condition.

**The trap, and why the first reading was discarded.** Immediately after `minikube start` returned,
the cluster reported:

```
todo-chatbot-backend   0/1  Completed   10   8d   <none>
todo-chatbot-frontend  0/1  Completed    1   8d   <none>
$ kubectl -n todo-chatbot wait --for=condition=available deploy --all
deployment.apps/todo-chatbot-backend condition met      <-- returned immediately
$ curl localhost:30080/login  ->  000
```

`kubectl wait --for=condition=available` returned **"condition met" while both apps were down**,
because it reads the Deployment's `Available` condition — which was still the **stale `True`
recorded 8 days earlier** and had not yet been reconciled by the restarted controller. The pods
were mid-transition (`Completed`, no IP) and the ports answered `000`.

**A naive automated T039 check would therefore have passed on a dead cluster.** The check is only
meaningful if it re-reads state after reconciliation *and* separately probes the ports — which is
why reachability is checked with `curl` rather than inferred from object status. Recorded because
T039's own done-condition ("yields a **working application**") is behavioral, and object status
alone does not establish it.

**Documentation defect found while re-verifying.** `README.md` §1 advertised the backend's OpenAPI
UI at `/docs`. It 404s. The routes are mounted under `settings.api_prefix`, which defaults to
`/api` (`backend-api/src/config/settings.py:29`), and `main.py` builds `docs_url` as
`f"{settings.api_prefix}/docs"` — so the real paths are `/api/docs` (200) and `/api/redoc`.
**Fixed in `README.md`.** A reader following the original line would have concluded the API was
misconfigured. Found only by actually requesting the documented URL.

### 5.9 The argument for T065 being a real run

**Eleven findings, none visible in review** — §5.1–§5.8 above, §5.10–§5.12 below. Almost all were
found only by executing the procedure, and one of those — §5.2 — was invisible until the cluster was
genuinely fresh, i.e. until exactly the state T065 defines. A README written but never followed is
not evidence, and neither is a script.

The last three were found **after** the deployment was reported healthy, by an owner exercising the
running application. Every automated check in this document passed while they were present. That is
the strongest available argument that T065 must be a real run and not a re-read.

### 5.10 The 500s: a four-layer defect chain

**Symptom (owner-reported, with DevTools evidence).** Sign-in worked. `POST /tasks` and
`POST /api/chat/send` both returned **500**. The database was confirmed up by the owner independently.

**Root cause analysis revealed four independent defects, each masking the next.**

#### Layer 1: `NEXT_PUBLIC_BACKEND_URL` inlined into server chunks

Four **server-side** call sites resolved the backend address with the build-time constant first:

```ts
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';
```

`NEXT_PUBLIC_*` is inlined by `next build`, so the first operand is a **string literal** at build
time. A truthy literal short-circuits the whole `||` chain, and Terser constant-folds it away —
`process.env.BACKEND_URL` is not merely shadowed, it is **deleted** from the bundle.

The consequence is the D6 trap one level down: inside the pod, `localhost:30800` is the **pod's own
loopback**, so the fetch fails `ECONNREFUSED`.

**Fix.** Remove `NEXT_PUBLIC_BACKEND_URL` from server code entirely. Server-side fetches should only
use `BACKEND_URL` (runtime), never the public variable. The browser path (`api-client.ts`) keeps it
because that code genuinely runs in the browser.

#### Layer 2: `BETTER_AUTH_URL` pointed to localhost:30080

The ConfigMap set `BETTER_AUTH_URL: "http://localhost:30080"` for the browser-facing origin. But
server-side code (server actions, route handlers) uses `BETTER_AUTH_URL` to fetch auth tokens from
the Better Auth API. Inside the pod, `localhost:30080` is the pod's own loopback — not the frontend
service.

**Fix.** Change `BETTER_AUTH_URL` in the ConfigMap to the in-cluster Service DNS:
`http://todo-chatbot-frontend:3000`. The browser-facing origin is already handled by
`NEXT_PUBLIC_BETTER_AUTH_URL` which is inlined for client-side code.

#### Layer 3: `channel_binding=require` in DATABASE_URL

The Neon connection string contained `channel_binding=require`, which the `asyncpg` library does not
support. The backend raised:

```
TypeError: connect() got an unexpected keyword argument 'channel_binding'
```

for every request that needed the database. This was masked by the earlier `ECONNREFUSED` errors
from the frontend — the backend was unreachable anyway.

**Fix.** Remove `channel_binding=require` from `DATABASE_URL` in `deploy/.env.deploy`. The backend
now connects successfully.

#### Layer 4: `minikube image load` and `helm upgrade` distribution defects

Documented in §5.11 and §5.12 below. Both were fixed in `deploy/deploy.sh` during diagnosis.

**Symptom (owner-reported, with DevTools evidence).** Sign-in worked. `POST /tasks` and
`POST /api/chat/send` both returned **500**. The database was confirmed up by the owner independently.

**Cause.** Four **server-side** call sites resolved the backend address with the build-time constant
first:

```ts
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';
```

`NEXT_PUBLIC_*` is inlined by `next build`, so the first operand is a **string literal** at build
time. A truthy literal short-circuits the whole `||` chain, and the minifier constant-folds it away —
`process.env.BACKEND_URL` is not merely shadowed, it is **deleted**. Verified inside the built image:
the server chunks contained `fetch(\`http://localhost:30800${a}\`, …)` and the identifier
`BACKEND_URL` appeared **nowhere** in `.next/server`.

The consequence is the D6 trap one level down: inside the pod, `localhost:30800` is the **pod's own
loopback**, so the fetch fails `ECONNREFUSED`. Server code must use in-cluster Service DNS.

**Why a chart-only fix cannot work.** The obvious response is to set `BACKEND_URL` in the ConfigMap.
It has no effect: the built server bundle contains no runtime lookup to influence. Confirmed by
rebuilding with the variable present and re-grepping — still absent. The defect is in the application
source, not the chart.

**Why sign-in masked it.** Better Auth's database path reads `DATABASE_URL`, a genuine **runtime**
variable supplied by `secretKeyRef`. It therefore worked, which made the deployment look half-healthy
and pointed suspicion at the database.

**The fix, and why it is not a redesign.** The very next line in the same files is *already correct*:

```ts
const AUTH_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000';
```

Runtime-first. The `BACKEND_URL` line was simply **inconsistent with its own neighbour**, and the
runtime-first ordering is proven working by that neighbour. Reordering restores the convention the
author already established; it does not invent one.

| Change | Where |
|---|---|
| Reorder to runtime-first | the 4 server call sites: `chat/actions.ts`, `tasks/actions.ts`, `api/chat/history/route.ts`, `api/chat/send/route.ts` |
| New `config.backendUrl` = `http://todo-chatbot-backend:7860` | `charts/todo-chatbot/values.yaml` |
| Expose it as `BACKEND_URL` | `charts/todo-chatbot/templates/configmap.yaml` |

`frontend/lib/api-client.ts` is **deliberately untouched** — it is the browser path and genuinely
needs the host-published address.

**Proof.** The rebuilt server bundle now reads:

```js
let y = process.env.BACKEND_URL || "http://localhost:30800",
    R = process.env.BETTER_AUTH_URL || "http://localhost:30080"
```

`process.env.BACKEND_URL` survives as a real runtime read, and the browser bundle still carries
`localhost:30800` (step 4's gate still passes). With the ConfigMap supplying the in-cluster
address, `POST /api/chat/send` returns **400** (empty body) and `POST /api/chat/history` returns
**405** (wrong method) instead of 500, and `ECONNREFUSED` no longer appears in the frontend log.

**Scope note.** This is a **third** application-source change beyond the two the plan authorized
(T024, T025). It was surfaced to the owner and approved before being made, because it expands the
phase's declared source-change set.

### 5.11 `minikube image load` silently no-ops when the tag already exists

**`deploy.sh` printed `✓ loaded both images into minikube` while the node kept the previous build.**

`minikube image load` does not overwrite an existing tag. It prints **nothing**, exits **0**, and
leaves the node's image untouched. Because the tag is the constant `dev`, the node's copy collides
with every later build. Measured directly:

```
host image  (freshly built, has the fix)  sha256:424a8cad…
pod running                               sha256:71500a13…   ← 8 days old
minikube image load todo-chatbot-frontend:dev   → silent, no output
node image AFTER the load                 sha256:71500a13…   ← UNCHANGED
```

The crash of the diagnosis was that the pod carried **new ConfigMap values with old code** — new
environment, previous binary — which excludes a configuration fault and points squarely at the image.

**It does not reproduce on a clean cluster**, where no tag exists to collide with. That is precisely
why the fresh-install path looked flawless and why this survived every prior verification: the defect
lives on the **update** path (FR-012, SC-009) only.

**Proof of mechanism.** Tagging the same image with a collision-free tag and loading that imports
correctly:

```
minikube image load todo-chatbot-frontend:t2
node image AFTER   sha256:a5830cbdfddf…   ← NEW
```

**Fix.** `deploy.sh` step 5 now drops the stale tag before loading. `-f` is required because a running
pod may still reference it; the container keeps running, it is only untagged.

### 5.12 `helm upgrade` does not roll pods, and `--set` persists

Two independent traps, both of which made a "successful" upgrade a no-op on the running workload.

**(a) No rollout.** The release advanced to a new revision and reported `deployed` while the pods
never restarted. Two reasons, and they compound:

- The image tag is the constant `dev`, so the pod template is **byte-identical** between two builds.
  Helm sees no template diff, so it creates no new ReplicaSet.
- Helm does not restart pods merely because a **ConfigMap** they mount has changed.

Evidence: one ReplicaSet per Deployment, both dated eight days earlier, after an upgrade that had
reported success. The corrected `BACKEND_URL` reached the live ConfigMap
(`kubectl get cm … -o jsonpath='{.data.BACKEND_URL}'` returned the new value) while the pod's
environment still lacked it — a configuration that is correct in the cluster and absent in the
process.

*(Helm's own mechanism here is defensible; the defect is that `deploy.sh` relied on it to deliver a
change it cannot deliver. Same family as §5.6 — correct behaviour, wrong expectation.)*

**Fix.** `deploy.sh` step 7 now runs `kubectl rollout restart deploy` followed by `rollout status`,
so what is running matches what was declared. On a fresh install this is a redundant but harmless
second rollout.

**(b) `--set` survives later upgrades.** Helm merges previous **user-supplied** values into every
subsequent upgrade. A one-off `--set frontend.image.tag=t2` therefore **persists**, so a later plain
`helm upgrade` silently keeps the override and ignores `values.yaml`:

```
helm get values todo-chatbot -n todo-chatbot
USER-SUPPLIED VALUES:
frontend:
  image:
    tag: t2
```

Observed as a revision that changed nothing, because the rendered template was identical. Recovered
with `--reset-values`. Not a defect in the deliverable — `deploy.sh` never passes `--set` — but
recorded because it is the trap a reader will fall into the moment they follow the obvious
diagnostic instinct and override a value on the command line.

---



## 6. 🔴 Credential exposure in backend logs on the startup-failure path (FR-007, T051)

**Reported because it was observed, not because it was looked for.** While diagnosing the
`CrashLoopBackOff` in §5, the backend's container log contained the **full `DATABASE_URL` including
the live Neon password**, in cleartext:

```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string
  '"postgresql://neondb_owner:<password>@ep-falling-sea-…neon.tech/neondb?…"'
```

### Mechanism

`backend-api/src/database.py:10` calls `create_async_engine(...)` at **import time**. When the URL
cannot be parsed, SQLAlchemy raises `ArgumentError` with the **raw string interpolated into the
message**. SQLAlchemy's usual protection — `URL.__repr__` masks the password as `***` — does not
apply here, because the string never became a `URL` object in the first place.

### Scope — deliberately stated, not overstated

| Path | Leaks? |
|---|---|
| **Normal operation** (valid URL) | ❌ No. No URL is logged; `URL.__repr__` masks the password in the connection errors that do occur. |
| **Malformed URL at startup** | ✅ **Yes** — the raw string, password included. |

So this is a **narrow but real** exposure, and it is reachable by exactly the misconfiguration
`§5.2`'s sibling defect produced. It fires only on the crash path, which is also the path a person
is most likely to be debugging in a shared terminal or pasting into a chat.

### Consequence for acceptance

- **T051's done-condition** ("the output contains **no credential values**") holds for the
  **steady-state** logs it inspects — the workloads are healthy and log no URL. It is **not** a
  universal property of this image.
- **FR-007** is therefore **conditionally satisfied**: the Deployment does not *write* secrets to
  logs, but a startup failure can cause the application's dependency to **echo** one.
- Reported rather than quietly fixed, because fixing it means changing `backend-api/src/database.py`
  — Phase III application code that Phase IV was scoped **not** to modify (T004/option A: four
  source changes, all in `frontend/`). A Phase IV-only fix would have to be a code change outside
  the accepted scope.

### Recommended remediation (not applied — needs an owner call)

Wrap the URL construction so the exception cannot carry it, or catch `ArgumentError` at import and
re-raise a message naming the **variable** rather than its value. Either is a small, contained
change — but it is a **fifth source change**, and this document does not authorise it.

### Also required regardless

**Rotate the Neon credential.** The value appeared in (a) the git history leak already recorded in
`security-scan.md` §3, and (b) now a container log and this session's transcript. Rotation is the
only remedy that makes either harmless.

---


