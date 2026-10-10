# Todo Chatbot — Phase IV: Local Kubernetes Deployment

Run the Phase III Todo Chatbot on a local Kubernetes cluster, from a machine that
has **nothing but Docker Desktop**. No Minikube, no Helm, no kubectl — installing
them is part of the procedure below, not a precondition.

Budget for the whole procedure on a clean machine: **under 60 minutes**,
toolchain installs included.

---

## 1. What you get

| Service | URL | Notes |
|---|---|---|
| Frontend | <http://localhost:30080> | The app. Sign in here. |
| Backend | <http://localhost:30800/health> | API. `/api/docs` for OpenAPI, `/api/redoc` for ReDoc. |

Two workloads from **one** Helm chart (`charts/todo-chatbot`), published on two
**pinned** NodePorts. The ports are not cluster-assigned — they are declared in
`charts/todo-chatbot/values.yaml`, and the deploy script reads them back out of
that file so the chart and the browser bundle cannot drift.

---

## 2. Prerequisites

- **Docker Desktop**, running. That is the only thing you must already have.
- ~6 GB free disk, ~4 GB free RAM.
- A terminal — **Git Bash** on Windows, or any POSIX shell.

Everything else is installed by §3.

---

## 3. The procedure

From the phase root:

```bash
cp deploy/.env.deploy.example deploy/.env.deploy
# edit deploy/.env.deploy and fill in the three real values
bash deploy/deploy.sh
```

That is the whole thing. The script is idempotent — **run it as many times as you
like**. The first run installs; every later run updates in place. There is no
"have I already installed this?" step to remember, because
`helm upgrade --install` is a single command that handles both cases.

### What the script does, in order

| Step | Action | Typical time |
|---|---|---|
| 1 | Verify Docker; install Minikube and Helm if absent | 2–10 min (first run only) |
| 2 | Start Minikube with the docker driver and the pinned ports | 2–5 min (first run only) |
| 3 | Build both images | 3–8 min (first run only) |
| 4 | **Prove** the declared ports landed in the browser bundle | seconds |
| 5 | Load both images into the cluster | 1–2 min |
| 6 | Materialize the `todo-chatbot-secrets` Secret from `.env.deploy` | seconds |
| 7 | `helm upgrade --install … --wait`, then print the URLs | 1–3 min |

`deploy/deploy.sh` is the documented procedure — it is not a convenience wrapper
around a hidden one. Every step above is a command you can read and run yourself.

### The three credentials

`deploy/.env.deploy` is **gitignored** and is the only place real credentials live
on disk. It never enters an image.

| Key | What it is |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL, pooled endpoint. One URL serves **both** services. |
| `BETTER_AUTH_SECRET` | Session/JWT signing secret. Used by **both** services. |
| `COHERE_API_KEY` | The chatbot's model provider key. Backend only. |

All three are referenced by the Deployments with `optional: false`. If one is
missing, the pod **fails to start and names the missing key** — it does not start
half-configured and fail later on the first request. See §6.

> **Quoting.** Values may be quoted or unquoted — `DATABASE_URL="postgres://…"`
> and `DATABASE_URL=postgres://…` both work. This is worth stating because
> `kubectl create secret --from-env-file` does **not** strip quotes the way Docker
> Compose does. Left alone, a quoted value ships its `"` characters into the
> Secret and the backend dies at startup with
> `Could not parse SQLAlchemy URL from string '"postgresql://…"'`. `deploy.sh`
> normalizes the file before building the Secret, and then verifies no stored
> value is quote-wrapped — so this cannot reach the cluster silently.

> **Note** — `backend-api/.env.example` names `GEMINI_API_KEY`. That variable is
> **not read by anything**; the agent reads `COHERE_API_KEY`
> (`backend-api/src/agents/agent_config.py`). `deploy/.env.deploy.example` has the
> correct name.

---

## 4. ⚠️ Changing a port requires rebuilding the frontend

> **This is the one thing that will bite you.**
>
> `NEXT_PUBLIC_BACKEND_URL` and `NEXT_PUBLIC_BETTER_AUTH_URL` are **build-time
> constants**. Next.js inlines them into the browser JavaScript during
> `next build`. They are *not* read at container start, and they are deliberately
> **not** in the ConfigMap.
>
> So if you edit `nodePort` in `charts/todo-chatbot/values.yaml` and then only
> re-run `helm upgrade`, the Services move but **the browser keeps calling the old
> port**. The app looks broken for no visible reason.
>
> **Correct response: re-run `bash deploy/deploy.sh`.** It re-reads the ports,
> rebuilds the frontend with the new values, and reloads the image. Step 4 of the
> script is a hard gate that fails the run if the declared ports are not actually
> present in the built bundle — so a stale image cannot be deployed silently.

Related: `frontend/lib/api-client.ts` falls back to `http://localhost:8000` when
`NEXT_PUBLIC_BACKEND_URL` is unset. The backend listens on **7860**. If the build
arg goes missing you get a dead-port failure that looks like an application bug.
Step 4 exists to catch exactly that.

---

## 5. Reaching the app from the host

The script starts Minikube with `--ports=30080:30080,30800:30800`, which publishes
both NodePorts to `localhost` with the same numbers. This is the primary mechanism,
and it is why the URLs in §1 work.

**If `http://localhost:30080` is not reachable** — some Docker Desktop / WSL
configurations do not forward published container ports to the Windows host — fall
back to port-forwarding, which publishes the **same port numbers**, so no image
needs rebuilding:

```bash
kubectl -n todo-chatbot port-forward --address 127.0.0.1 svc/todo-chatbot-frontend 30080:3000
kubectl -n todo-chatbot port-forward --address 127.0.0.1 svc/todo-chatbot-backend  30800:7860
```

Keep both running in a spare terminal. The script prints these two lines for you
when it detects the ports are not reachable.

> A port-forward is a **host-side process**. If it dies, the app becomes
> unreachable even though every pod is healthy — check it first before debugging
> the cluster.

---

## 6. Operating it

```bash
kubectl -n todo-chatbot get pods -o wide          # what is running
kubectl -n todo-chatbot get svc                   # the pinned NodePorts
kubectl -n todo-chatbot logs deploy/todo-chatbot-backend
kubectl -n todo-chatbot logs deploy/todo-chatbot-frontend
kubectl -n todo-chatbot describe pod <pod>        # events, probe failures
```

### Scale

```bash
kubectl -n todo-chatbot scale deploy/todo-chatbot-backend --replicas=3
```

Scaling needs no other artifact edited. Scale-down is graceful: a `preStop` hook
withdraws the pod from Service rotation before shutdown, and
`terminationGracePeriodSeconds: 60` gives an in-flight chat turn time to finish
rather than being SIGTERMed mid-stream.

### Replacing a credential

Edit `deploy/.env.deploy`, re-run `bash deploy/deploy.sh`, then restart the
workloads so they re-read the Secret:

```bash
kubectl -n todo-chatbot rollout restart deploy
```

**No image is rebuilt.** The credential scan commands in §8 confirm the value
never entered one.

### How many backend replicas will this node hold?

The node's capacity is the `minikube start` allocation from §3. Memory is the
binding constraint:

| | CPU | Memory |
|---|---|---|
| Node allocatable (`--cpus=4 --memory=3584`) | ≈ 3.9 cores | ≈ 2.9 GiB |
| `kube-system` baseline | ≈ 0.5 cores | ≈ 0.6 GiB |
| Frontend, worst case (1 replica + 1 rolling surge) | 0.2 cores | 0.5 GiB |
| **Remaining for the backend** | **≈ 3.2 cores** | **≈ 1.8 GiB** |
| Backend request *per replica* | 100m | 256Mi |
| **Backend replicas this node supports** | 32 | **≈ 7** |

**Stated maximum: 7 backend replicas**, memory-bound.

> The `--memory` value is capped by Docker Desktop's own allocation (Settings →
> Resources). This host reports 3854 MB, so `minikube start` rejects 4096 with
> `MK_USAGE`; the script uses 3584 to leave the host headroom. If you raise Docker
> Desktop's memory, raise `MEMORY` in `deploy/deploy.sh` — this table scales with it.

Confirm the two measured inputs on your own node — everything below them is
arithmetic from `charts/todo-chatbot/values.yaml`:

```bash
kubectl describe node minikube | grep -A6 'Allocatable'
kubectl -n kube-system top pods            # if metrics-server is available
```

Changing the requests in `values.yaml` changes this number. If you change them,
change this section.

> <sub>**Footnote — connection budget.** The Neon pooled endpoint allows 901
> concurrent connections. Each backend replica holds a pool of 8 and each frontend
> replica holds one of 10, so the constraint is `8·B + 10·F ≤ 901`. At the stated
> maximum (B=7, F=1) that is 66 of 901 — **not binding**. Memory runs out long
> before connections do; the budget is recorded here only so the limit is not
> rediscovered the hard way.</sub>

---

## 7. Where AI assisted

Per the Phase IV requirements, AI tooling assisted where it genuinely helped, and
the results were verified rather than trusted:

- **Docker AI — Gordon (`docker ai`)** — assisted with the container image work:
  the multi-stage `frontend/Dockerfile` and the `.dockerignore` hardening. Every
  suggestion was checked against an actual build and an actual `docker run` before
  being kept.
- **Claude Code** — authored the Helm chart, the deploy procedure, and the
  environment contract; ran `helm lint` and `helm template` to verify the chart
  renders exactly the intended objects and nothing else.
- **Not used: `kubectl-ai` and `kagent`.** Neither is installed on this host, and
  **no acceptance criterion depends on them.** The deployment does not assume they
  exist. See `history/prompts/local-kubernetes-deployment/` for the record of each
  AI-assisted operation and which assistant was used.

---

## 8. Credential scan

**Nothing to install.** This uses only `git`, `grep`, `tar` and `docker` — all
already present. (TruffleHog, gitleaks and `docker scout` are deliberately *not*
used: the first two are not installed, and `scout` reports CVEs, not credentials.)

Scope is the **repository** — git-tracked files and git history — plus **both
built images**. Untracked working files (`.env`, `.env.*`, all gitignored) are out
of scope.

```bash
P='AIza[0-9A-Za-z_-]{35}|npg_[A-Za-z0-9]{8,}|postgres(ql)?://[^:]+:[^@]+@|sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'

git grep -nIE "$P"                       # tracked files
git log -p --all | grep -nIE "$P"        # history — including deleted lines

# both images
for img in todo-chatbot-backend:dev todo-chatbot-frontend:dev; do
  rm -rf /tmp/scan && mkdir -p /tmp/scan
  docker save "$img" -o /tmp/scan/img.tar
  tar -xf /tmp/scan/img.tar -C /tmp/scan
  grep -rlIE "$P" /tmp/scan && echo "HIT in $img" || echo "clean: $img"
done
```

Run the same literal-value search for the project's own secrets — the Neon
password, `BETTER_AUTH_SECRET`, `COHERE_API_KEY` — with `grep -F` (they contain
regex metacharacters), and `git log --all -S'<value>' --oneline` to find the commit
that introduced a value even if it was later deleted.

> 🔴 **Check the layer format before trusting a clean image result.** The loop
> above finds plaintext inside uncompressed `layer.tar` entries. If Docker emits
> **gzipped** layers (OCI layout), a plain `grep` reports *clean* on a compressed
> blob — a **false negative**. Decompress first:
>
> ```bash
> find /tmp/scan -name '*.tar.gz' -exec sh -c \
>   'tar -xzOf "$1" | grep -aIE "'"$P"'" && echo "HIT $1"' _ {} \;
> ```

---

## 9. Tear down

```bash
helm uninstall todo-chatbot -n todo-chatbot
kubectl delete namespace todo-chatbot
minikube delete                     # removes the whole cluster
```

`minikube delete` followed by §3 is the clean-state path, and it is the run that
proves this README is complete: everything here should work from an empty cluster
with nothing but `.env.deploy` filled in.

---

## 10. Layout

```
charts/todo-chatbot/          one chart, two workloads
  Chart.yaml
  values.yaml                 single source of truth — ports, replicas, resources
  templates/
    _helpers.tpl
    serviceaccount.yaml
    configmap.yaml            non-sensitive config only (D6)
    backend-deployment.yaml   optional:false secret refs → fail-fast
    frontend-deployment.yaml
    backend-service.yaml      NodePort 30800 → 7860
    frontend-service.yaml     NodePort 30080 → 3000
    NOTES.txt
deploy/
  deploy.sh                   the documented procedure
  .env.deploy.example         placeholder template (committed)
  .env.deploy                 real credentials (GITIGNORED — never commit)
frontend/Dockerfile           multi-stage, non-root, standalone output
frontend/.dockerignore        🔒 keeps .env out of the image
```

The chart creates **no RBAC objects**, and both pods run with
`automountServiceAccountToken: false`, a read-only root filesystem, all
capabilities dropped, and `runAsNonRoot` at UID 1000.
