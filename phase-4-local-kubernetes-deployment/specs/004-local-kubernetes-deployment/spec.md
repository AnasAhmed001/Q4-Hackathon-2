# Feature Specification: Phase IV — Local Kubernetes Deployment of the Todo Chatbot

**Feature Branch**: `004-local-kubernetes-deployment`
**Created**: 2026-09-15
**Status**: Draft
**Input**: User description: "Using our project constitution and the Phase IV requirements, draft spec.md for deploying the Todo Chatbot (from Phase III) to a local Kubernetes cluster.

GOAL
Enable the existing Todo Chatbot (frontend + backend + AI agent) to run as a set of containerized services on a local Kubernetes cluster, so that the full application can be started, stopped, scaled, and inspected using standard Kubernetes tooling instead of running processes directly on the host machine.

USER SCENARIOS
- When a developer runs the deployment command, both frontend and backend come up as running pods without manual intervention.
- When a developer scales the backend to multiple replicas, the chatbot continues to function correctly and requests are distributed across pods.
- When a pod crashes or is deleted, Kubernetes restarts it automatically and the app becomes available again without manual redeployment.
- When a developer inspects the cluster, they can see pod health, logs, and resource usage for both services.

FUNCTIONAL REQUIREMENTS
1. Frontend and backend must each be packaged as a separate Docker image, built from this repository's existing source.
2. Both services must be deployable to a local Minikube cluster via Helm charts.
3. The backend must expose its API on a stable in-cluster service address that the frontend can reach regardless of which pod is currently running.
4. Environment-specific configuration (API keys, database URL, service URLs) must be injected via Kubernetes ConfigMaps/Secrets, not hardcoded into the image.
5. The Helm chart must expose configurable replica counts for both frontend and backend.
6. The deployed app must be reachable from the host machine's browser (via Minikube service/tunnel or NodePort) with no additional manual networking steps beyond what's documented in the README.
7. A single documented command (or short sequence) must build the images, load them into Minikube, and install/upgrade the Helm release.

EDGE CASES & RULES
- If a required secret/config value is missing at deploy time, the pod must fail to start with a clear error rather than starting in a broken state.
- If the backend pod is not yet ready, the frontend must not crash — it should show a loading/error state until the backend becomes reachable.
- Re-running the deploy command on an existing release must upgrade it in place, not create duplicate/conflicting resources.
- Scaling replicas up or down must not cause data loss or duplicate task processing.

OUT OF SCOPE
- Cloud deployment (DigitalOcean/AKS/GKE) — that's Phase V.
- Kafka, Dapr, or any event-driven architecture — Phase V.
- CI/CD pipelines — Phase V.
- Any new chatbot features beyond what Phase III already implements.

ACCEPTANCE CRITERIA
- [ ] `docker build` succeeds for both frontend and backend images.
- [ ] `helm install` deploys both services to Minikube with zero manual kubectl edits afterward.
- [ ] `kubectl get pods` shows both services Running and Ready.
- [ ] The chatbot is reachable and functional from a browser via the Minikube-exposed URL.
- [ ] Scaling the backend replica count (via Helm values) actually changes the running pod count.
- [ ] Killing a pod manually results in Kubernetes recreating it automatically.
- [ ] README documents the exact commands to reproduce the deployment from a clean Minikube cluster.

Describe behavior and outcomes only — no Dockerfile syntax, no Helm template internals, no specific YAML structure. That belongs in the plan phase."

## Overview

Phase III delivered a working Todo AI Chatbot that runs as processes on a developer's host machine. This feature **re-hosts** that application — unchanged in behavior — as a set of containerized workloads on a local Kubernetes cluster, so the full system can be started, stopped, scaled, and inspected with standard cluster tooling rather than host processes.

This is a **deployment and operations** feature, not a product feature. It adds no new user-facing capability. Its value is that the Phase III product becomes reproducible, self-healing, and operable.

**The two workloads involved:**

| Workload | What it is | Phase III responsibility |
|----------|-----------|--------------------------|
| **Frontend** | The browser-facing web application (sign-in, task pages, chat interface) | Serves the UI, holds sessions, and forwards privileged calls to the backend |
| **Backend** | The service hosting the AI agent and its task tools | Serves the task API and the conversational AI agent |

Both use the same external managed database that Phase III already uses. That database is **not** deployed into the cluster by this feature.

---

## Clarifications

### Session 2026-09-15

- Q: Which local cluster is authoritative for Phase IV, and is installing its toolchain part of the documented procedure? → A: **Minikube is the authoritative cluster, and installing Minikube + Helm is a documented step inside the procedure** — not an assumed prerequisite. A genuinely clean machine must reach a working application by following the README top to bottom.
- Q: What is the host-visible exposure mechanism, and is the resulting browser-facing address fixed and knowable before the image build? → A: **NodePort with declared (pinned) port numbers, reached at a stable `localhost` host.** The browser-facing URLs are therefore known before the image build, no hosts-file entry is required, and the host does not change when the cluster is recreated.
- Q: Is AI-assisted ops tooling (Gordon, kubectl-ai, kagent) a requirement this spec must encode, and at what strength? → A: **Docker AI (Gordon) is mandatory and named; kubectl-ai and kagent are best-effort.** The phase brief's own fallback (standard CLI or Claude Code, recorded) applies where a tool is unavailable. No acceptance criterion may depend on kubectl-ai or kagent, so no in-cluster agent controller enters scope.
- Q: Which database does the deployed cluster actually talk to? → A: **The existing external managed provider, but a separate database or branch dedicated to Phase IV** — same schema, isolated data. Both workloads connect to it directly. This keeps verification runs repeatable and non-destructive while leaving the schema unforked.
- Q: What does "clean cluster" / "clean environment" concretely mean for the acceptance criteria? → A: **The toolchain is present; the cluster is deleted and recreated; the application is not installed.** Canonical definition — a *clean state* is: the host has the toolchain available (re-installing it is a no-op), `minikube delete` then `minikube start` has produced a freshly created cluster, any addons the procedure requires have been enabled **by the procedure itself rather than assumed**, and no Helm release for this application is installed. No acceptance criterion may use "clean" to mean a machine lacking the toolchain (SC-001's clean-*machine* claim is verified separately and once, per FR-022) or a cluster that already has the application installed.
- Q: SC-004 names no scanner and SC-010 names no metrics source. What proves each of them? → A: **SC-004 is proved by a named scanner over tracked files, git history, and both built images; SC-010 is proved by declared resource boundaries read back from the cluster.** SC-010 does **not** require live consumption metrics, so **no cluster metrics addon enters scope** and none may be assumed present. For SC-004, untracked working-tree files — notably `.env`, verified gitignored and untracked — are explicitly out of scope; "the repository" means what git tracks, including history.
- Q: May two installations coexist on one cluster, and what happens when a second deploy collides? → A: **Exactly one installation per cluster.** A second deployment that would collide — by release name, namespace, or pinned host-visible port — MUST be detected and refused with an explicit error naming the conflicting value, rather than failing cryptically. Multi-developer shared clusters are deferred to a later phase.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bring the whole application up with one documented procedure (Priority: P1)

A developer with a clean machine and no prior cluster state follows a single documented procedure. The application's components are packaged, loaded into the local cluster, and started. The developer then opens the exposed address in a browser, signs in, and successfully manages tasks by chatting in natural language — exactly as in Phase III, but now served from cluster workloads rather than host processes.

**Why this priority**: This is the MVP. Without a working end-to-end deployment, no other scenario in this feature can be demonstrated. It is also the scenario that proves constitution principle II (reproducibility from a clean state) and success criterion SC-007 (re-hosted, not rebuilt).

**Independent Test**: Starting from a clean cluster, execute the documented procedure exactly as written, then open the exposed URL in a browser, authenticate, and complete one full conversational task operation (e.g. create a task by chat and confirm it appears). Fully delivers value on its own: the application is running on the cluster and usable.

**Acceptance Scenarios**:

1. **Given** a clean local cluster with no application installed, **When** the developer runs the documented deployment procedure once, **Then** both the frontend and backend workloads reach a running-and-ready state with no additional manual cluster edits.
2. **Given** the deployment has completed, **When** the developer opens the documented address in a host browser, **Then** the application UI loads and the developer can authenticate.
3. **Given** the developer is authenticated in the browser, **When** they send a natural-language message to the chatbot that creates or queries a task, **Then** the chatbot responds correctly and the effect is visible in the task list.
4. **Given** the application is running on the cluster, **When** the developer follows only the documented steps to stop and restart it, **Then** the application returns to a working state without undocumented intervention.

---

### User Story 2 - The platform self-heals from workload failure (Priority: P2)

A pod is deleted or a workload crashes. Without any developer action, the cluster recreates the affected workload, and the application becomes available again. The developer never has to redeploy or restart anything by hand.

**Why this priority**: This is the primary operational benefit of moving to a cluster, and the direct expression of constitution principle VI (operational readiness) and success criterion SC-002. It demonstrates that recovery is owned by the platform rather than by the developer's memory.

**Independent Test**: With the application healthy, terminate a running instance of each workload in turn. Observe that replacement instances start automatically and the application serves requests again, with no manual redeployment.

**Acceptance Scenarios**:

1. **Given** the application is running and healthy, **When** a running backend instance is terminated, **Then** a replacement instance starts automatically and the chatbot is functional again without manual intervention.
2. **Given** the application is running and healthy, **When** a running frontend instance is terminated, **Then** a replacement instance starts automatically and the UI is reachable again without manual intervention.
3. **Given** a workload is starting or restarting, **When** the developer checks the application's health, **Then** the workload's readiness state accurately reflects whether it can serve traffic, and traffic is not routed to an instance that is not yet ready.

---

### User Story 3 - Scale the backend without breaking the chatbot (Priority: P3)

A developer increases or decreases the declared number of backend instances. The running instance count changes to match, and the chatbot continues to behave correctly — requests are spread across instances, conversation history remains consistent, and no task operation is applied twice.

**Why this priority**: This validates that the Phase III architecture (stateless request handling, database-backed conversation and task state) genuinely holds under a clustered deployment. It is the scenario most likely to expose hidden per-process state, so it is high-value verification even though it is not required for the MVP.

**Independent Test**: Change only the declared replica count, apply it, confirm the running instance count matches, then drive a conversational workload and confirm responses remain correct and no operation is duplicated.

**Acceptance Scenarios**:

1. **Given** the application is running with one backend instance, **When** the developer raises the declared replica count, **Then** the number of running backend instances increases to match, with no other artifact edited.
2. **Given** the application is running with multiple backend instances, **When** the developer lowers the declared replica count, **Then** the number of running backend instances decreases to match and the chatbot remains functional.
3. **Given** multiple backend instances are running, **When** a user holds a multi-turn conversation and performs task operations, **Then** conversation context is preserved across turns and each requested operation is applied exactly once.
4. **Given** the backend is scaled up or down, **When** the developer inspects task and conversation data afterwards, **Then** no data loss and no duplicate task entries are present.

---

### User Story 4 - Inspect, operate, and update the deployment (Priority: P4)

A developer inspects the running application: it can see the health of each workload, read their logs, and observe their resource consumption. They can re-run the deployment procedure to apply a change, and it updates the existing installation in place rather than creating a second, conflicting one. They can adjust declared resource boundaries.

**Why this priority**: Constitution principle VI requires that status, logs, and resource boundaries be observable and declared for every workload. This makes the deployment operable rather than merely running. It depends on the earlier stories being in place.

**Independent Test**: With the application running, retrieve status, logs, and resource usage for both workloads without restarting or altering them; then re-run the deployment procedure and confirm an in-place update with no duplicated resources.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** the developer requests current workload status, **Then** the health and readiness of every instance of both services is reported without any change to the running workloads.
2. **Given** the application is running, **When** the developer requests logs, **Then** logs for both services are retrievable without restarting or modifying the workloads.
3. **Given** the application is running, **When** the developer requests resource usage, **Then** consumption for both services is observable.
4. **Given** an installation already exists, **When** the developer re-runs the documented deployment procedure, **Then** the existing installation is updated in place, with no duplicate or conflicting resources created.
5. **Given** a developer changes a declared resource boundary, **When** the procedure is re-applied, **Then** the workloads adopt the new boundary without the application being removed and recreated.

---

### Edge Cases

- **Required configuration missing at deploy time**: If a required config or secret value is absent when the deployment is applied, the affected workload MUST fail to start and report an explicit, human-readable error naming the missing item. It MUST NOT start in a half-configured state and fail later on first user request.
- **Backend not yet ready when the frontend starts**: The frontend MUST NOT crash or serve a broken page. It MUST present a loading or error state and begin working once the backend becomes reachable — without the frontend being restarted.
- **Re-running the deployment on an existing installation**: MUST perform an in-place update. It MUST NOT create a second installation, duplicate resources, or leave the previous version's resources orphaned.
- **A second installation is attempted on the same cluster**: The procedure MUST detect the collision — an existing release, an occupied namespace, or a pinned host-visible port already in use — and MUST fail with an explicit error naming the conflicting value. It MUST NOT partially deploy, silently overwrite the existing installation, or fail with an opaque low-level error (FR-028).
- **Scaling up or down**: MUST NOT cause data loss, lost conversations, or duplicate task processing. Requests in flight during a scale-down MUST either complete or fail cleanly — never be applied twice.
- **Application images not available to the cluster**: If images are not present where the cluster can obtain them, the workloads fail to start. The documented procedure MUST handle making images available so a clean-cluster run does not require undocumented image-transfer steps.
- **The browser-facing address is fixed at image-build time**: Both browser-visible URLs are compile-time constants in the frontend bundle, so the address MUST be declared before the images are built rather than discovered after deployment. Changing a declared port MUST therefore be treated as requiring a frontend image rebuild, and the documented procedure MUST state that. No deployed resource may be hand-edited to correct the address.
- **The host-visible path depends on a host-side process staying alive**: Reaching the workloads at a `localhost` address depends on a long-running host-side process (or equivalent) that the developer starts. If it stops or is interrupted, the application becomes unreachable from the browser even though every workload is healthy. The procedure MUST document this dependency, and the application MUST recover once the process is restored, without redeploying.
- **Database unreachable, credentials invalid, or connection limit reached**: Workloads MUST surface an explicit, readable error rather than restarting indefinitely with no diagnosable message. A connection-limit rejection caused by scaling MUST be distinguishable from a credential or network failure, so it is not mistaken for an application defect.
- **Cluster stopped and restarted** (e.g. the local cluster is shut down and started again — a *stopped-and-restarted* cluster, not a recreated one): The application MUST return to a working state by re-running the documented start procedure, without re-running the build or re-installing from scratch. Note this is a distinct case from the **clean state** of SC-005, where the cluster is deleted and recreated.
- **A required cluster addon is not enabled**: Where the procedure depends on a cluster addon, it MUST enable that addon itself and MUST NOT assume a default cluster has it. A run against a freshly created cluster MUST NOT fail because an addon the procedure needs was left disabled.
- **One service updated while the other is not**: During an in-place update, a temporarily mismatched pair of versions MUST NOT corrupt data or leave the application permanently broken; the end state must be a consistent, working application.
- **Multiple browser users at once**: Concurrent users MUST continue to see only their own tasks and conversations, exactly as in Phase III — the clustering must not weaken per-user isolation.

---

## Requirements *(mandatory)*

### Functional Requirements

**Packaging and deployment**

- **FR-001**: The frontend and the backend MUST each be packaged as its own container image, built from this repository's existing source. No application behavior may be reimplemented for the purpose of deployment.
- **FR-002**: Both services MUST be deployable to a local Kubernetes cluster — **Minikube specifically** — as a single named installation, applied as one declarative unit.
- **FR-003**: Every artifact that defines a workload, its configuration, or its exposure MUST exist as a version-controlled declarative file. Direct manual mutation of the running cluster MUST NOT be the delivery mechanism for any change; where manual steps are used for diagnosis, the resulting change MUST be back-ported to source.

**Connectivity**

- **FR-004**: The backend MUST be reachable by the frontend at a stable in-cluster address that does not depend on which individual backend instance is serving a request.
- **FR-005**: The backend MUST also be reachable from the host browser, because at least one existing client-side page calls the backend directly rather than through the frontend's server. Its browser-facing address MUST be a declared `localhost` address with a pinned port number, knowable before the frontend image is built.
- **FR-006**: The application MUST be reachable from the host machine's browser at a declared `localhost` address over NodePort, with **no hosts-file entry and no networking step beyond those documented**. The port numbers MUST be declared values, not assigned by the cluster.

**Configuration**

- **FR-007**: All environment-specific configuration — API keys, database connection details, service addresses, authentication secrets, and allowed origins — MUST be supplied at deploy time and MUST NOT be embedded in the images, committed to the repository, or written to logs.
- **FR-008**: Each credential MUST be replaceable without rebuilding any image.
- **FR-009**: Declared replica counts for both the frontend and the backend MUST be configurable without editing any template or source file.

**Failure behavior**

- **FR-010**: When a required configuration or secret value is missing, the affected workload MUST fail fast with an explicit error naming the missing item, rather than starting in a degraded state.
- **FR-011**: When the backend is unavailable or not yet ready, the frontend MUST remain running and present a loading or error state, then recover automatically once the backend becomes reachable — without requiring a frontend restart.
- **FR-012**: Re-applying the deployment to an existing installation MUST update it in place, creating no duplicate or conflicting resources.
- **FR-013**: Scaling the backend up or down MUST NOT cause data loss, lost conversation context, or duplicate application of any task operation.

**Operability**

- **FR-014**: Every workload MUST declare a health signal that the platform uses to judge readiness, so that traffic is not routed to an instance that cannot serve it and unhealthy instances are replaced.
- **FR-015**: Every workload MUST declare explicit resource boundaries, so that no workload can consume unbounded cluster resources.
- **FR-016**: Current status and logs for both services MUST be obtainable without restarting or modifying the running workloads.
- **FR-017**: Workloads MUST run with only the permissions they require, and MUST NOT be granted cluster-wide permissions by default.

**Preservation of Phase III**

- **FR-018**: Every Phase III conversational capability MUST remain functional after deployment: creating, viewing, updating, completing, and deleting tasks by natural language, and resuming prior conversations. This is a re-hosting, not a rebuild.
- **FR-019**: Per-user data isolation and the existing authorization behavior MUST be preserved unchanged.
- **FR-020**: The application MUST continue to use the **existing external managed database provider**, with the **same schema**. Both the frontend and the backend connect to it directly. Phase IV MUST target a **separate database or branch dedicated to this phase**, so that verification runs are repeatable and non-destructive against Phase III data. This feature MUST NOT migrate, fork, or restructure the schema.

**Reproducibility and evidence**

- **FR-021**: A single documented procedure (or short sequence) MUST build the images, make them available to the cluster, and install or update the installation. Where the cluster toolchain itself (Minikube, Helm) is absent, installing it is part of this procedure rather than a prerequisite assumed of the reader.
- **FR-022**: The documented procedure MUST be executable end-to-end from a clean machine and a clean state (see Clarifications, Session 2026-09-15) with no undocumented prerequisites — including no assumption that Minikube, Helm, or a running Docker daemon are already present, and no assumption that any addon is pre-enabled — and MUST have been executed that way at least once before the feature is declared complete.
- **FR-023**: Differences between the local environment and any future target environment MUST be expressed purely as configuration values, never as differences in artifact structure or topology.
- **FR-024**: Every AI-assisted operation performed during this phase MUST be traceable to a retained record of the prompts used and iterations taken, under `history/`.
- **FR-025**: Docker AI (Gordon, invoked as `docker ai`) MUST be used for the container operations it supports, and MUST be named in the documented procedure. Where Gordon is unavailable in a given environment, the documented fallback is the standard Docker CLI or Claude Code, and the substitution MUST be recorded under `history/`.
- **FR-026**: `kubectl-ai` and `kagent` SHOULD be used where available, but MUST NOT be a precondition of any acceptance criterion. Their absence MUST NOT block deployment or verification, and the documented procedure MUST remain executable end-to-end without them. Any in-cluster agent controller or observability stack they would install is **out of scope** for this feature.
- **FR-027**: The declared backend replica count MUST be compatible with the target database's connection limits. Scaling MUST NOT exhaust the database's connection budget, and the documented procedure MUST state the maximum declared replica count the current configuration supports.
- **FR-028**: Exactly **one** installation may exist per cluster. Where a second deployment would collide with an existing one — by release name, namespace, or pinned host-visible port — the procedure MUST detect the collision and fail with an explicit error naming the conflicting value. It MUST NOT produce a partial deployment or a cryptic low-level failure.

### Key Entities

- **Installation**: The single named, declaratively applied unit that owns all resources for this application. Identified by a name and a namespace. Re-applying it updates it in place. **Exactly one installation may exist per cluster**; a second one that would collide is refused with an explicit error (FR-028).
- **Workload (Frontend, Backend)**: A deployable service with a declared instance count, declared resource boundaries, a declared health signal, and an image reference. Two exist: frontend and backend.
- **Container Image**: A versioned, self-contained artifact built from this repository's source for one service. Contains no secrets. Two exist: one per service.
- **Configuration Set**: The deploy-time-supplied values a workload needs — non-sensitive settings and sensitive credentials held separately, so that credentials are never mixed into general configuration.
- **Service Address**: A stable network identity for a workload inside the cluster, used by the frontend to reach the backend independent of instance identity.
- **Exposed Endpoint**: The host-machine-visible address through which a browser reaches the frontend and the backend.
- **Deployment Procedure**: The documented, ordered command sequence that takes a clean machine and clean cluster to a running, browser-reachable application — and that is also the update path for an existing installation.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer starting from a clean machine and a **clean cluster** (as defined in Clarifications, Session 2026-09-15) reaches a working, browser-accessible chatbot by following one documented procedure, in **under 60 minutes**, with **zero undocumented prerequisites**. Because toolchain installation is a step in the procedure, the 60-minute budget **includes** installing Minikube and Helm.
- **SC-002**: After an unplanned termination of any workload instance, the application returns to a healthy, serving state **automatically, with zero manual steps**, within **2 minutes**.
- **SC-003**: Changing the declared instance count for either service changes the number of running instances to match, **without editing any other artifact**.
- **SC-004**: A credential scan reports **zero credentials**. "The repository" means **git-tracked files and git history**; untracked working-tree files — notably `.env`, which is gitignored and untracked today — are explicitly **out of scope**. Both built images are scanned. The scanner MUST be named in the documented procedure and installed by it if absent, so the criterion is verifiable from a clean machine without an undocumented tool.
- **SC-005**: The full acceptance procedure passes from a **clean state** (as defined in Clarifications, Session 2026-09-15 — toolchain present, cluster deleted and recreated, application not installed), **reproducibly, on two consecutive runs**, each run beginning from that same clean state.
- **SC-006**: **100% of Phase III conversational capabilities** remain functional after deployment — create, view, update, complete, and delete tasks by natural language, plus conversation resumption — with **no behavioral regression**.
- **SC-007**: With the backend deliberately made unavailable, the application shows a loading or error state rather than crashing, and recovers **automatically, without a restart**, once the backend returns.
- **SC-008**: Deploying with a required configuration value omitted causes the affected service to **refuse to start** and report an explicit error identifying the missing item — **0%** of the time does it start and fail later on first use.
- **SC-009**: Re-running the documented procedure on an existing installation completes as an in-place update, leaving **exactly the declared** set of running instances and resources — **zero duplicates, zero orphans**.
- **SC-010**: An operator can retrieve current status, logs, and resource usage for both services **without restarting or modifying** them. **"Resource usage" means each workload's declared resource boundaries (requests and limits) read back from the cluster — not live consumption metrics.** No cluster metrics addon is required by this feature, and none may be assumed present.

- **SC-011**: Every container operation in the documented procedure is attributable to a retained record under `history/`, naming the assistant used — Docker AI (Gordon) where available, and the recorded fallback otherwise.

---

## Assumptions

Documented defaults adopted where the input did not specify a choice. Each is a reasonable-default decision, not a requirement handed down.

1. **Both services belong to one installation.** The stated acceptance criterion `helm install` deploys *both* services, so this spec treats the application as a single named installation that owns both workloads, rather than two independently installed units.
2. **The external managed database stays external.** The input names a database URL as deploy-time configuration and places cloud deployment out of scope. The database is therefore consumed, not deployed, by this feature. Clarified (Session 2026-09-15): the target is a **separate database or branch on the same provider**, not Phase III's live data, so that repeatable verification does not mutate live contents.
3. **The AI provider is an external dependency.** The chatbot's model provider is reached over the network with a deploy-time credential. No model is hosted in the cluster.
4. **The backend is stateless across requests.** This is what makes User Story 3 achievable, and it matches the Phase III design in which conversation and task state live in the database. This feature verifies that property rather than introducing it.
5. **Local cluster is single-node.** The input specifies a local cluster for development. Multi-node scheduling behavior is not a requirement, though nothing here should prevent it.
6. **Two workloads, not three.** Inspection of the existing source found the AI agent and its task tools to be in-process within the backend service, so no third deployable component is introduced.
7. **The frontend has a server side.** The frontend is not a static bundle: it hosts sessions and proxies privileged calls to the backend. Its deployment must therefore run a server, and its configuration must be present before it starts.
8. **The browser-facing address is a declared, build-time value.** At least one browser-side code path depends on a value that is fixed when the frontend is built rather than when it starts. This was resolved during clarification (Session 2026-09-15): the host-visible address is a declared `localhost` address with pinned port numbers, so it is knowable before the build. *How* those pinned ports are wired to the workloads remains a plan-phase decision.
9. **Verification is manual and recorded.** The acceptance criteria are verified by running documented commands and observing results, with the evidence retained — consistent with constitution principle VII.
10. **Existing Phase III sources are the starting point.** Images are built from what is already in this repository. Where a service lacks packaging today, packaging is added; the application code itself is not redesigned.

---

## Out of Scope

Explicitly excluded. Each is deferred to a later phase or is simply not part of this work.

- **Cloud deployment** — managed or cloud-hosted clusters. The input defers this to Phase V.
- **Event-driven architecture** — message brokers or distributed application runtimes. Deferred to Phase V.
- **CI/CD pipelines** — automated build, test, and release automation. Deferred to Phase V.
- **New chatbot or product features** — anything beyond what Phase III already implements. This feature re-hosts; it does not extend. If a capability is missing from Phase III, it stays missing here.
- **Application data migration or restructuring** — the existing database **schema and provider** are used as-is. The *contents* target a Phase IV-specific database or branch (FR-020), not Phase III's live data.
- **High availability across nodes, autoscaling policies, and production-grade ingress** — the target is a local development cluster.
- **Observability stacks** — dedicated metrics, tracing, or log-aggregation platforms. Only the cluster's built-in inspection capability is required. This exclusion also covers any in-cluster agent controller introduced by `kagent` (see FR-026). **No metrics addon is needed**: SC-010 is satisfied by declared resource boundaries read back from the cluster, not by live consumption metrics.
- **`kubectl-ai` and `kagent` as hard dependencies** — they are optional tooling. The documented procedure must work without them, and no acceptance criterion is contingent on them.
- **Multi-environment configuration management** — only the local environment must work; portability must be *possible* (FR-023), not exercised.
- **Multi-developer shared clusters** — more than one installation, or more than one developer, against a single cluster. This phase assumes one installation per cluster (FR-028); coexistence is deferred to a later phase.
- **Authentication changes** — Phase III authentication and per-user isolation are preserved, not modified.

---

## Dependencies

- **Phase III source** — the existing frontend and backend in this repository, which define all application behavior.
- **The existing external managed database** — a database or branch dedicated to Phase IV on the existing provider (FR-020). It must remain reachable from the cluster, accept connections from it, and hold **both** workloads' credentials: the frontend needs direct database access for authentication state, not only the backend.
- **Database connection budget** — the provider's connection limit must accommodate the declared maximum backend replica count plus the frontend, allowing for pooling (FR-027).
- **An AI model provider credential** — the chatbot cannot respond without it; it is deploy-time configuration.
- **Docker AI (Gordon)** — available in this environment as the `docker ai` CLI plugin (v1.17.1, Docker Desktop). Used for the container operations it supports (FR-025). `kubectl-ai` and `kagent` are **not** installed and are not depended upon (FR-026).
- **A local Kubernetes cluster and its toolchain** — **Minikube is the authoritative cluster** for this phase. Minikube and Helm are **not** assumed to be present: installing them is a step in the documented procedure (see Clarifications, Session 2026-09-15). A running container runtime is likewise not assumed.
- **Container image build capability** — a container runtime usable by the documented procedure.

---

## Risks

- **Build-time-fixed browser configuration vs. deploy-time-assigned addresses.** *(Resolved during clarification: the address is now a declared value known before the build, so it no longer depends on a cluster-assigned address.)* The residual risk is that changing a declared port silently requires a frontend image rebuild — a developer who edits the port and re-applies without rebuilding will see a browser that cannot reach the backend, and the symptom will look like an application bug rather than a stale build.
- **The one client-side backend call path.** It is easy to satisfy the in-cluster address requirement and still leave this page broken, because it fails only when a user opens that specific page. It needs its own explicit verification step.
- **Secret sprawl across two services.** Both services need overlapping credentials — confirmed during clarification, and worse than it first appears: **the frontend also needs direct database access**, because authentication state lives in the database. If configuration is assembled ad hoc, values will drift between them and one service will fail in a way that looks like an application bug. A further concrete hazard exists today: `backend-api/.dockerignore` correctly excludes `.env`, but `frontend/` has **neither a Dockerfile nor a `.dockerignore`**, so a frontend image built without one would bake `frontend/.env` — including the auth secret and database URL — into the image, which SC-004 would then catch.
- **Local cluster image availability.** A clean-state run fails at the least obvious point if images are not made available to the cluster; this must be part of the documented procedure, not tribal knowledge.
- **The host-visible address depends on a host-side process.** Because the exposure decision pins ports on a `localhost` host, browser reachability depends on a long-running host-side process staying alive. If it dies, the application looks down while every workload is healthy — a failure that mimics an application outage. It needs its own verification step and a documented recovery path.

---

## Acceptance Checklist

Mirrors the acceptance criteria supplied in the input, restated as verifiable outcomes.

- [ ] Both service images build successfully from this repository's source.
- [ ] One declarative apply installs both services to the local cluster with **zero manual cluster edits afterwards**.
- [ ] Both services report **running and ready**.
- [ ] The chatbot is reachable and functional from a host browser via the documented exposed address, including the client-side page that calls the backend directly (FR-005).
- [ ] Changing a declared replica count actually changes the running instance count for both services.
- [ ] Terminating an instance results in automatic recreation and restored service.
- [ ] Re-applying the deployment updates in place, with no duplicate resources.
- [ ] The README documents the exact commands to reproduce the deployment from a clean state — toolchain present, cluster deleted and recreated, no application installed — including any addon the procedure requires.
- [ ] A credential scan of the repository and images reports zero credentials.
- [ ] Every AI-assisted operation is recorded under `history/` with the assistant named, Gordon included (SC-011).
- [ ] The full procedure has been executed end-to-end from a clean state and the evidence retained.
