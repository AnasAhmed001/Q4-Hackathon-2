---
id: 003
title: Phase IV Kubernetes Deployment Task Breakdown
stage: tasks
date: 2026-09-24
surface: agent
model: deepseek-v4-flash
feature: local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: /sp.tasks
labels: ["tasks", "phase-iv", "kubernetes", "minikube", "helm", "neon-mcp", "spec-traceability", "ambiguity-flags"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-local-kubernetes-deployment/tasks.md
  - history/prompts/local-kubernetes-deployment/003-phase-iv-cluster-deployment-task-breakdown.tasks.prompt.md
tests:
  - bash .specify/scripts/bash/check-prerequisites.sh --json (run; FAILED with "Feature directory not found: Q4-Hackathon-2/specs/004-local-kubernetes-deployment" — the pre-documented specs-root mismatch; FEATURE_DIR resolved by hand instead)
  - find specs/004-local-kubernetes-deployment -type f (run; confirmed research.md, data-model.md, quickstart.md and contracts/ do NOT exist despite plan.md listing them)
  - grep -rn NEXT_PUBLIC_BACKEND_URL|NEXT_PUBLIC_BETTER_AUTH_URL frontend/ (run; confirmed the one client-side direct call path)
  - grep -rn "api-client" frontend/app frontend/components frontend/lib (run; sole importer is app/(protected)/tasks/[id]/edit/page.tsx:5, a 'use client' component)
  - cat frontend/lib/auth-server.ts (run; confirmed pg.Pool with process.env.DATABASE_URL at lines 6-15 — frontend direct DB access)
  - git check-ignore -v frontend/.env (run; confirmed gitignored via frontend/.gitignore:34)
  - git ls-files | grep -i env|dockerignore|Dockerfile (run; confirmed no .env tracked, frontend has no Dockerfile/.dockerignore)
  - docker --version; docker ai --version; minikube version; helm version; kubectl version --client; neonctl --version; trufflehog --version (run; minikube, helm, neonctl, trufflehog all ABSENT)
  - curl "https://mcp.neon.tech/api/list-tools?category=branches" (run; enumerated exact Neon MCP tool names and schemas)
  - curl "https://mcp.neon.tech/api/list-tools?category=querying" (run; confirmed run_sql contract)
  - awk + grep format validation over tasks.md (run; 68 tasks, IDs T001-T068 sequential, every task has a Done-when line, no malformed checklist lines)
---

## Prompt

```text
Using the finalized spec.md and the approved plan.md, break the Phase IV 
work into an ordered, checkable task list.

Organize tasks by user story priority (P1 → P4), matching spec.md's 
structure:
- P1: Bring the whole application up with one documented procedure
- P2: The platform self-heals from workload failure
- P3: Scale the backend without breaking the chatbot
- P4: Inspect, operate, and update the deployment

For each user story's tasks:
- Make P1 fully self-contained and independently testable first — it's the 
  MVP and every later story builds on it being deployable.
- Each task should be small enough to verify on its own against a specific 
  requirement or acceptance criterion from spec.md (reference the FR-### 
  or SC-### it satisfies).
- Include the two things flagged as unresolved before this: (a) confirming 
  whether the frontend needs direct database access and a second exposed 
  backend port (verify against actual Phase III source before building 
  anything on top of that assumption), and (b) deciding and implementing 
  how the Phase IV database branch is reset or reseeded between clean-state 
  verification runs.
- Include the pre-flight collision check (FR-028) as its own task, not 
  folded into the general Helm chart task.
- Include the credential scan (SC-004) and the two consecutive clean-state 
  verification runs (SC-005) as explicit final tasks, not assumed to happen 
  automatically.

Do not write implementation code yet. After each task, note what "done" 
looks like — the specific command or observation that proves it — so I can 
check it off against the spec as we go, not just against your own judgment.

Flag any task where the plan was ambiguous about the approach, rather than 
guessing and moving on.
```

### Follow-up prompt (same workstream — mechanism selection for the two unresolved items)

```text
For T004 (plan Q1) and T009: Neon MCP is already installed and available in 
this environment. Use it directly to provision the `phase-iv` branch from 
the existing project's default branch — do not install neonctl or use manual 
console steps. Record the MCP tool call and its output under history/ per 
FR-024/SC-011.

For T010: check whether the Neon MCP exposes a branch reset (copy-on-write) 
or delete+recreate tool. If it does, use that as the SC-005 reset mechanism 
instead of a TRUNCATE script — same requirement (single documented command, 
idempotent, verifiable as empty before a verification run), just via the 
MCP tool rather than a shell script.

Re-render T009 and T010 with this mechanism and confirm neither task still 
requires neonctl to be installed.
```

## Response snapshot

Generated `specs/004-local-kubernetes-deployment/tasks.md`: **68 tasks, T001–T068**, in seven phases —
Setup, Foundational (blocking), then one phase per user story in priority order (P1→P4), then Polish.
Every task carries the `FR-###`/`SC-###` it satisfies and a **"Done when"** line giving the exact command
or observation that proves it. Task-ID distribution: Setup 5, Foundational 22, US1 14, US2 4, US3 4,
US4 8, Polish 11.

**Pre-flight re-verification of the two unresolved assumptions — both CONFIRMED against Phase III source
before any task was built on them:**
1. **Frontend needs direct database access** — ✅ CONFIRMED. `frontend/lib/auth-server.ts:6-15` builds
   `new Pool({ connectionString: process.env.DATABASE_URL })` and passes it as `database: pool`. So
   `DATABASE_URL` is a **frontend runtime** Secret key, not backend-only.
2. **Frontend needs a second exposed backend port** — ✅ CONFIRMED. `frontend/lib/api-client.ts:31` reads
   `NEXT_PUBLIC_BACKEND_URL`; its **only** importer is
   `frontend/app/(protected)/tasks/[id]/edit/page.tsx:5`, a `'use client'` component. This is FR-005 and
   exactly the single "client-side call path" of spec Risk #2. No second path exists.

**Two findings the plan did not anticipate:** (a) `api-client.ts` falls back to `http://localhost:8000`
while the backend listens on **7860**, so an unbaked `NEXT_PUBLIC_BACKEND_URL` fails on the same page as
a stale bundle — mitigation in T034/T037; (b) `plan.md` lists `research.md`, `data-model.md`,
`quickstart.md` and `contracts/*` as inputs, but **none of them exist** — they became tasks (T006,
T059–T061) rather than assumed inputs.

Requested items were each made their own task as instructed: **FR-028 pre-flight collision check** (T028,
split from the four non-collision preflight checks in T029), **SC-004 credential scan** (T064), and the
**two consecutive clean-state runs** (T065, T066) — with T010's branch reset explicitly feeding both.

**Follow-up applied — Neon MCP mechanism resolved.** Tool names and signatures were read from the live
server's unauthenticated tool listing (`https://mcp.neon.tech/api/list-tools?category=branches`) rather
than from prose docs, which name only categories. T009 re-rendered to use `get_default_branch` →
`create_branch` → `get_connection_string` → `describe_branch` → `run_sql`; T010 re-rendered to use
`list_branches` → `reset_from_parent` → `run_sql`. **Neither task requires `neonctl`** — it now appears in
the document only as a recorded absence and an explicit "not to be installed".

Three hazards surfaced during that work and were written into the tasks:
- **TTL hazard**: `neon.ts` declares a branch policy auto-expiring new non-default branches at `ttl: "7d"`.
  A `phase-iv` branch created via `neon checkout` would **silently vanish mid-phase**, breaking SC-005's
  second run. T009 now requires verifying `expires_at` and clearing it via `update_branch`.
- **Destructive-tool constraint**: the MCP marks `reset_from_parent` and `delete_branch` as requiring
  explicit user confirmation ("NEVER run autonomously"). T010 specifies a confirmation step rather than a
  silent automated call.
- **Reset semantics**: `reset_from_parent` resets to the **parent's current HEAD**, not to the branch's
  creation point. If `main` accumulates Phase III data, every clean-state reset re-imports it into the
  Phase IV branch — putting Phase III data in the branch at the exact moment SC-005 is certified. T010's
  `run_sql` emptiness check is the detector; the mitigation is flagged as undecided rather than guessed.

## Outcome

- ✅ Impact: `tasks.md` is complete and executable — 68 tasks, all traceable to spec requirements, each
  with an objective completion check. Two of the three items the owner flagged as unresolved at plan time
  are now **closed** (FR-005 direct-call path; frontend DB access — both confirmed by source), and the
  third (database branch lifecycle) now has a concrete MCP mechanism rather than a candidate list.
- 🧪 Tests: No application tests written (deployment feature; spec requests no TDD). Verification is
  spec-acceptance-based: T064 (SC-004 scan), T065/T066 (SC-005 two consecutive clean-state runs),
  T067 (acceptance-checklist sweep with captured evidence). Format validation run mechanically over
  `tasks.md` — 68/68 well-formed checklists, sequential IDs, every task with a Done-when line.
- 📁 Files: `specs/004-local-kubernetes-deployment/tasks.md` (created); this PHR.
- 🔁 Next prompts: `/sp.analyze` to cross-check spec ↔ plan ↔ tasks for gaps; then resolve open decision
  **T002** (the `.specify` specs-root mismatch) before `/sp.implement`, because it will block the same
  way it blocked this command. **T004** now needs only Q2 (Neon connection limit) and Q3 (scanner).
- 🧠 Reflection: The highest-value output was not the task list but the two source re-verifications and the
  MCP contract inspection. Reading the live tool listing instead of the docs page turned three unknowns
  (does a reset tool exist? what are its parameters? does it need a branch id or a name?) into a written
  contract — and surfaced the `neon.ts` TTL policy, which would have silently deleted the Phase IV branch
  partway through the phase. The plan's assertion of "zero rows of Phase III production data" on the parent
  branch remains **unverified** and is the one premise still resting on faith; T009 step 5 tests it.

## Evaluation notes (flywheel)

- Failure modes observed:
  1. `.specify/scripts/bash/check-prerequisites.sh --json` **failed** (exit 1) — resolves the specs root
     from `git rev-parse --show-toplevel`, which is the *parent* directory here. Pre-documented in
     `checklists/requirements.md` and still unfixed; `/sp.tasks` required solving for FEATURE_DIR by hand.
     Now tracked as task T002 because `/sp.implement` will hit it identically.
  2. `.specify/scripts/bash/create-phr.sh` **failed** ("PHR template not found at .specify/templates/ or
     templates/") — same root cause. PHR written agent-native per the documented fallback.
  3. Python is unavailable on this host (`python -c` → Microsoft Store alias error); validation scripts
     were written in `awk`/`grep` instead.
  4. A trap in the MCP tool listing: passing `readonly=true` **to the listing endpoint** makes it report
     the server as read-only and omit all write tools. Re-queried without the parameter to read the actual
     configuration. Worth remembering — the first read of this endpoint is misleading.
  5. `plan.md` cites four documents that do not exist. Caught by `find`, not by reading the plan.
- Graders run and results (PASS/FAIL): Format grader — **PASS** (68/68 tasks match
  `- [ ] T### [P?] [Story?] description — refs`; IDs sequential T001–T068; no malformed lines).
  Done-when grader — **PASS** (every task has a completion check).
  Traceability grader — **PASS** (every task names at least one `FR-###`/`SC-###`, or is explicitly
  marked as tooling/evidence with no FR).
  Ambiguity-discipline grader — **PASS** (7 flagged items in a dedicated table; no unflagged guess found).
- Prompt variant (if applicable): n/a — single `/sp.tasks` invocation with one follow-up redirect.
- Next experiment (smallest change to try): Before `/sp.implement`, resolve T002 by adding a root-level
  `specs` link so the `.specify` scripts resolve correctly. It is a one-line fix that unblocks every
  subsequent `/sp.*` command, and its absence has now cost time in two consecutive phases (evidence: the
  empty `Q4-Hackathon-2/history/prompts/001-todo-ai-chatbot/` directory noted in the spec checklist).
