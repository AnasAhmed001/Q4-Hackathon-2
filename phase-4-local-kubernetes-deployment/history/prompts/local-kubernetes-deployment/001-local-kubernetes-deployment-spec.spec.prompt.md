---
id: 001
title: Phase IV Kubernetes Deployment Specification Created
stage: spec
date: 2026-09-15
surface: agent
model: deepseek-v4-flash
feature: local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: /sp.specify
labels: ["spec", "phase-iv", "kubernetes", "helm", "minikube", "containerization", "deployment"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-local-kubernetes-deployment/spec.md
  - specs/004-local-kubernetes-deployment/checklists/requirements.md
  - history/prompts/local-kubernetes-deployment/001-local-kubernetes-deployment-spec.spec.prompt.md
tests:
  - .specify/scripts/bash/check-prerequisites.sh --json (run to verify branch/feature-dir resolution; twice)
  - git rev-parse --show-toplevel (run to confirm repo root is the parent directory, not the phase dir)
  - git ls-files | grep -i env + git check-ignore (run to confirm no credentials are tracked in source)
---

## Prompt

```text
Using our project constitution and the Phase IV requirements, draft spec.md 
for deploying the Todo Chatbot (from Phase III) to a local Kubernetes cluster.

GOAL
Enable the existing Todo Chatbot (frontend + backend + AI agent) to run as a 
set of containerized services on a local Kubernetes cluster, so that the full 
application can be started, stopped, scaled, and inspected using standard 
Kubernetes tooling instead of running processes directly on the host machine.

USER SCENARIOS
- When a developer runs the deployment command, both frontend and backend 
  come up as running pods without manual intervention.
- When a developer scales the backend to multiple replicas, the chatbot 
  continues to function correctly and requests are distributed across pods.
- When a pod crashes or is deleted, Kubernetes restarts it automatically and 
  the app becomes available again without manual redeployment.
- When a developer inspects the cluster, they can see pod health, logs, and 
  resource usage for both services.

FUNCTIONAL REQUIREMENTS
1. Frontend and backend must each be packaged as a separate Docker image, 
   built from this repository's existing source.
2. Both services must be deployable to a local Minikube cluster via Helm charts.
3. The backend must expose its API on a stable in-cluster service address that 
   the frontend can reach regardless of which pod is currently running.
4. Environment-specific configuration (API keys, database URL, service URLs) 
   must be injected via Kubernetes ConfigMaps/Secrets, not hardcoded into the 
   image.
5. The Helm chart must expose configurable replica counts for both frontend 
   and backend.
6. The deployed app must be reachable from the host machine's browser 
   (via Minikube service/tunnel or NodePort) with no additional manual 
   networking steps beyond what's documented in the README.
7. A single documented command (or short sequence) must build the images, 
   load them into Minikube, and install/upgrade the Helm release.

EDGE CASES & RULES
- If a required secret/config value is missing at deploy time, the pod must 
  fail to start with a clear error rather than starting in a broken state.
- If the backend pod is not yet ready, the frontend must not crash — it should 
  show a loading/error state until the backend becomes reachable.
- Re-running the deploy command on an existing release must upgrade it 
  in place, not create duplicate/conflicting resources.
- Scaling replicas up or down must not cause data loss or duplicate task 
  processing.

OUT OF SCOPE
- Cloud deployment (DigitalOcean/AKS/GKE) — that's Phase V.
- Kafka, Dapr, or any event-driven architecture — Phase V.
- CI/CD pipelines — Phase V.
- Any new chatbot features beyond what Phase III already implements.

ACCEPTANCE CRITERIA
- [ ] `docker build` succeeds for both frontend and backend images.
- [ ] `helm install` deploys both services to Minikube with zero manual 
      kubectl edits afterward.
- [ ] `kubectl get pods` shows both services Running and Ready.
- [ ] The chatbot is reachable and functional from a browser via the 
      Minikube-exposed URL.
- [ ] Scaling the backend replica count (via Helm values) actually changes 
      the running pod count.
- [ ] Killing a pod manually results in Kubernetes recreating it 
      automatically.
- [ ] README documents the exact commands to reproduce the deployment 
      from a clean Minikube cluster.

Describe behavior and outcomes only — no Dockerfile syntax, no Helm template 
internals, no specific YAML structure. That belongs in the plan phase.



also i have created a new branch named local-kubernetes-deplyment and also switched to it so no need to create a new branch
```

## Response snapshot

Produced `specs/004-local-kubernetes-deployment/spec.md`, grounded in the project constitution (v3.0.0) and in first-hand inspection of the Phase III source rather than assumption.

**Reconnaissance performed before drafting.** Read `.specify/memory/constitution.md`, the Phase III spec (`specs/001-todo-ai-chatbot/spec.md`), `backend-api/Dockerfile`, `backend-api/requirements.txt`, `frontend/package.json`, `frontend/proxy.ts`, `frontend/lib/api-client.ts`, and `.specify/scripts/bash/{create-new-feature,common,check-prerequisites}.sh`. Enumerated every environment variable the two services actually consume by grepping the source.

**Findings that changed the spec:**

1. **Branch name broke the SDD toolchain.** `common.sh` requires feature branches to match `^[0-9]{3}-`. Verified by running `check-prerequisites.sh --json`, which returned `ERROR: Not on a feature branch`. A branch lacking a numeric prefix also makes `find_feature_dir_by_prefix()` fall back to exact directory matching. Raised with the user; the user deleted the branch and authorised a new one from `main`. Created `004-local-kubernetes-deployment`.

2. **A client-side page calls the backend from the browser.** `frontend/lib/api-client.ts` resolves its base URL from `NEXT_PUBLIC_BACKEND_URL` (build-time inlined), and it is imported by the `'use client'` page `app/(protected)/tasks/[id]/edit/page.tsx`. A browser cannot resolve an in-cluster DNS name, so an in-cluster-only backend would leave that page broken — which conflicts with constitution SC-007 ("re-hosted, not rebuilt"). Put to the user as a scope decision; the user chose to expose the backend to the host as well. Captured as FR-005 plus a dedicated edge case, a success criterion, and Assumption 8.

3. **The AI agent is in-process.** `backend-api/src/mcp/` sits inside the backend service, so there are two deployable workloads, not three. Recorded as Assumption 6.

4. **Both services share the database but need overlapping, distinct credentials** (the frontend talks to the database directly for authentication). Recorded as a named risk.

5. **`.env.example` files contain real-looking credentials** in the backend directory. Confirmed **untracked** (`git ls-files` matches only `backend-api/alembic/env.py`; both `.env` patterns are gitignored), so SC-004 is not currently violated — but flagged so the values are not swept into a committed artifact during implementation.

**Spec structure delivered:** Overview with a two-workload table; four prioritised user stories (P1 one-procedure bring-up, P2 self-healing, P3 scale-without-breakage, P4 inspect/operate/update), each with independent tests and Given/When/Then scenarios; ten edge cases; twenty-four functional requirements grouped into Packaging, Connectivity, Configuration, Failure behaviour, Operability, Preservation of Phase III, and Reproducibility; seven key entities; ten measurable success criteria (SC-001–SC-010); ten documented assumptions; an eight-item out-of-scope list; dependencies; four risks; and an acceptance checklist mirroring the input.

**Constitution alignment:** each Phase IV constitution success criterion (SC-001–SC-007) maps onto a spec success criterion — clean-machine reproducibility, automatic recovery, values-only environment differences, zero committed credentials, reproducible acceptance passing, AI-operation traceability, and unchanged Phase III behaviour.

**Deliberate exclusion of implementation detail,** per the user's instruction: no Dockerfile syntax, no chart/template internals, no YAML structure. Framework names for the application itself were stripped from the Overview and replaced with functional descriptions; Kubernetes, Helm, and Minikube are retained because they are the named subject of the feature.

## Outcome

- ✅ Impact: Phase IV has an approved-shape specification grounded in verified repository facts. Two scope decisions that would otherwise have surfaced mid-implementation (branch naming, backend browser reachability) were resolved before any code was written.
- 🧪 Tests: No application tests run — this is a specification stage. Verification consisted of executing the SDD prerequisite script (surfacing the branch-name blocker), confirming the git toplevel is the parent directory, and confirming no credentials are tracked.
- 📁 Files: Created `specs/004-local-kubernetes-deployment/spec.md`, `specs/004-local-kubernetes-deployment/checklists/requirements.md`, and this PHR. Created branch `004-local-kubernetes-deployment` from `main`.
- 🔁 Next prompts: Resolve the repo-root/specs-root mismatch (see below), then `/sp.plan`. Consider `/sp.clarify` if the two inferred scope boundaries — one installation owning both workloads, and two workloads rather than three — need explicit confirmation.
- 🧠 Reflection: The most valuable output of this stage was not the document but the reconnaissance. Both blockers were invisible from the requirements text and only appeared by reading the source and running the project's own scripts. A spec drafted purely from the prompt would have been internally consistent and wrong in two places.

## Evaluation notes (flywheel)

- Failure modes observed: The user's stated premise ("i have created a new branch ... so no need to create a new branch") was itself the defect — the branch existed but could not satisfy the workflow that would consume its spec. Trusting a stated premise about tooling state over the tooling's own output would have propagated the error into `/sp.plan`.
- Graders run and results (PASS/FAIL): Spec quality checklist (`checklists/requirements.md`) — PASS on all 16 items, zero `[NEEDS CLARIFICATION]` markers. Branch/prerequisite check — FAIL initially, PASS after branch recreation.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Before the next SDD command in any phase directory of this repository, run `bash .specify/scripts/bash/check-prerequisites.sh --json` first. It is a two-second check that reliably predicts whether the command will work, and it caught a structural blocker here that reading the requirements could not.

## Outstanding blocker for the next stage

`/sp.plan` and `/sp.tasks` call `setup-plan.sh` and `check-prerequisites.sh`, which resolve the specs root from `git rev-parse --show-toplevel`. In this repository that is the **parent** directory (`Q4-Hackathon-2`), so those scripts look for `Q4-Hackathon-2/specs/004-local-kubernetes-deployment` and will report *"Feature directory not found"* even though the spec exists under `phase-4-local-kubernetes-deployment/specs/004-local-kubernetes-deployment/`.

Corroborating evidence that this pre-dates the current work: `Q4-Hackathon-2/history/prompts/001-todo-ai-chatbot/` exists at the repo root but is **empty** — the residue of an earlier run that rooted at the parent and created a directory nothing ever used.

Needs a one-line resolution before `/sp.plan`: either a `specs` link at the repository root pointing at this phase's `specs/`, or the phase directory becoming its own repository root. Not resolved unilaterally because both options change repository layout.
