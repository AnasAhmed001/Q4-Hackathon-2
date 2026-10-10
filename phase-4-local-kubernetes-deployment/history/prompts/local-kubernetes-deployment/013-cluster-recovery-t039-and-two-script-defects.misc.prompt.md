---
id: 013
title: Cluster recovery, T039 restart verification, and two script defects
stage: misc
date: 2026-10-09
surface: agent
model: deepseek-v4-flash
feature: 004-local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: /sp.implement
labels: ["t033", "t035", "t039", "recovery", "defect", "curl", "readme", "fr-003", "fr-006", "fr-012"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - deploy/deploy.sh
 - README.md
 - specs/004-local-kubernetes-deployment/tasks.md
 - specs/004-local-kubernetes-deployment/research.md
 - history/prompts/local-kubernetes-deployment/013-cluster-recovery-t039-and-two-script-defects.misc.prompt.md
tests:
 - docker inspect minikube --format '{{json .NetworkSettings.Ports}}'
 - helm list -n todo-chatbot
 - kubectl -n todo-chatbot get pods -o wide
 - curl -s -o /dev/null -w '%{http_code}' http://localhost:30080/login
 - curl -s -o /dev/null -w '%{http_code}' http://localhost:30800/health
 - bash -n deploy/deploy.sh
 - minikube stop && minikube start
---

## Prompt

**"try again"**

(Verbatim. Sent 2026-10-09, eight days after the previous session. The deployment had been left
`STATUS: deployed`, revision 3, both pods `1/1`, both ports 200.)

## Response snapshot

Diagnosed why the app was unreachable, restored it **without rebuilding or reinstalling**, used the
recovery as the T039 test, and found and fixed two defects along the way.

### 1. Diagnosis — the app was down because Docker Desktop was down

Nothing had regressed in the deliverable. Docker Desktop had been closed, and since the Minikube
cluster *is* a container inside it, the whole stack went with it:

| Check | Result |
|---|---|
| Docker daemon | **DOWN** — `npipe:////./pipe/dockerDesktopLinuxEngine` not found |
| Minikube | `status error` — cannot reach the Docker API |
| helm / kubectl | `cluster unreachable` |
| ports | no response |

Confirmed by `docker ps -a`: `minikube  Exited (137) 8 days ago` — matching when Docker Desktop
went down.

### 2. Restoration — `minikube start`, no build, no install

Resumed the **existing** profile in 2m27s. Everything persisted: published ports still bound to
`0.0.0.0:30080` and `0.0.0.0:30800`, helm still `REVISION: 3 / STATUS: deployed`, pods `AGE 8d`.
Both ports returned **200**. The app renders: `<title>Sign In | Task Manager</title>`, Email and
Password fields, 56 `_next/static` asset references.

### 3. T039 — PASS (and a trap worth recording)

Ran T039's literal sequence, `minikube stop` → `minikube start`. Same result: deployments `1/1
AVAILABLE`, both ports 200, **no build and no install**, helm still revision 3.

**The first reading was discarded.** Immediately after `minikube start`, `kubectl wait
--for=condition=available` reported **"condition met" while both apps were down** — it read a
**stale `Available=True` from 8 days earlier** that the restarted controller had not reconciled.
Pods showed `0/1 Completed` with no IPs and the ports answered `000`. **A naive automated T039
check would have passed on a dead cluster.** Re-verified after reconciliation and probed
independently with `curl`, which is what the behavioural done-condition requires.

### 4. Defect — `deploy.sh` step 2 false-alarmed on a healthy app

`if curl -sS -o /dev/null -m 5 …; then` tests curl's **exit status**. Under Git Bash with
`-o /dev/null`, curl returns **23 (`CURLE_WRITE_ERROR`) even on HTTP 200** — measured `http=200
curl_rc=23`. The else-branch therefore fired for a working frontend, printing
`not reachable yet` and pointing the reader at the port-forward fallback for a non-problem. It had
in fact fired on two earlier runs that were both up.

Proven side by side against the live app: **OLD form → "NOT reachable"; NEW form → "reachable
(HTTP 200)"**. Fixed by testing the **HTTP code** (written to stdout regardless of the write error),
with `|| true` so the non-zero status cannot poison the pipeline under `set -e`. `bash -n` clean.

Same family as §5.1 (pipefail + `grep -c`): a POSIX tool's exit status is not always the signal
you want, and `set -e`/`pipefail` silently convert the mismatch into a wrong branch.

### 5. Defect — `README.md` §1 documented a 404

The README advertised the backend's OpenAPI UI at `/docs`. It **404s**. Routes are mounted under
`settings.api_prefix`, defaulting to `/api` (`backend-api/src/config/settings.py:29`), and
`main.py` builds `docs_url` as `f"{settings.api_prefix}/docs"`. Verified: `/api/docs` 200,
`/api/redoc` 200, `/api/openapi.json` 200. **Fixed in the README.** A reader following the original
line would have concluded the API was misconfigured.

### 6. Tasks marked

**T033**, **T035**, **T039** → `[x]`, each with its done-condition and, where a clause could not be
met literally, that fact stated rather than glossed:

- **T033** — `--ports` confirmed supported on the docker driver (ports published to `0.0.0.0`, and
  they survive a cluster restart). The plan-time `⚠️ AMBIGUOUS` marker is now `✅ RESOLVED`, with
  the original hedge retained in the record.
- **T035** — met, but **two clauses reported as-written rather than as-met**: "`git status` clean"
  is unsatisfiable (the Phase IV deliverable *is* the uncommitted change set) and "no `kubectl
  apply` in the transcript" is literally false (deploy.sh applies the namespace and Secret
  declaratively). `kubectl edit` was never used and no cluster object exists that is not rendered
  by the chart or built by the script.

## Outcome

- ✅ Impact: cluster restored with zero rebuild/reinstall; T033/T035/T039 closed with honest
  evidence; two defects fixed (one script, one documentation).
- 🧪 Tests: `bash -n` clean; old-vs-new curl comparison against a live app; documented URLs probed;
  ports/helm/pods re-verified after restart.
- 📁 Files: `deploy/deploy.sh`, `README.md`, `tasks.md`, `research.md` (§5.7 curl, §5.8 restart +
  README, §5.9 conclusion).
- 🔁 Next prompts: **T036/T037 (browser — require the owner)**, then T038, T040, T041, T064, T065,
  T067.
- 🧠 Reflection: both new defects were found by *contradiction* — a warning that disagreed with a
  measurement taken seconds earlier, and a documented URL that 404'd. Neither is visible in review,
  and the second had been sitting in the README through a full prior verification pass.

## Evaluation notes (flywheel)

- Failure modes observed: a GUI dependency (Docker Desktop) taking the whole stack down silently;
  a stale Kubernetes condition making an automated readiness check report success on a dead
  cluster; curl's exit status diverging from the HTTP response under Git Bash.
- Graders run and results (PASS/FAIL): T039 PASS (behavioural, curl-probed, after reconciliation).
  T033 PASS. T035 PASS with two clauses recorded as not-literally-met.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): have T065's acceptance sweep probe ports with `curl`
  rather than trusting `kubectl wait`, per §5.8.
