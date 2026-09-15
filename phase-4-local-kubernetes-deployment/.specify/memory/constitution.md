<!--
Sync Impact Report
==================
Version change: 2.1.0 → 3.0.0 (MAJOR)
Bump rationale: The constitution was redefined to govern principles, practices, and
  governance ONLY. Every technical specification section was removed, and principles
  that previously bound implementation choices were rewritten at the practice level.
  This is a backward-incompatible redefinition of the constitution's scope.

Modified Principles (old → new):
  I.   Stateless Architecture   → I.   Declarative & Version-Controlled State
  II.  MCP-First                → II.  Reproducibility from a Clean State
  III. User-Scoped              → III. Environment Parity & Portability
  IV.  Production-Ready         → IV.  AI-Assisted Operations with Captured Evidence
  V.   Testing Discipline       → V.   Security & Configuration Hygiene
  (new)                         → VI.  Operational Readiness
  (new)                         → VII. Verification & Evidence Discipline
  (new)                         → VIII. Spec-Driven Traceability

Added Sections:
  - Constitution Scope & Boundaries (explicitly excludes technical specifications)
  - Phase IV Success Criteria (outcome-level and measurable)

Removed Sections (content relocated to feature specs and plans):
  - Technology Stack (Non-Negotiable)
  - Database Models (Fixed)
  - API Endpoint
  - Code Quality Standards
  - Deployment Standards
  - Development Workflow

Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md  - no edit required; Constitution Check is
     generic and defers to this file
  ✅ .specify/templates/spec-template.md  - no edit required; no constitution coupling
  ✅ .specify/templates/tasks-template.md - no edit required; no constitution coupling
  ✅ .claude/commands/sp.*.md             - reviewed; no principle-specific references
  ✅ .opencode/commands/sp.*.md           - reviewed; no principle-specific references

Follow-up TODOs: None
-->

# Todo AI Chatbot — Phase IV Constitution
## Local Cluster Deployment: Declarative, Reproducible, AI-Assisted Operations

## Core Principles

### I. Declarative & Version-Controlled State

Every artifact that defines an environment, a workload, or a piece of configuration MUST
exist as a version-controlled declarative file. Changes to a running environment MUST
originate from source and be applied through a repeatable process. Direct manual mutation
of a live environment is PROHIBITED as a delivery mechanism. Where manual intervention is
used for diagnosis, the resulting change MUST be back-ported to source before the work is
considered complete.

**Rationale**: If it is not in source, it cannot be reviewed, reproduced, or rolled back.

### II. Reproducibility from a Clean State

A new contributor MUST be able to reach a fully working environment from a clean machine
by following documented, automated steps. No step may depend on undocumented
prerequisites, on prior machine state, or on knowledge held only by the original author.
Every documented procedure MUST be executed end-to-end from a clean state at least once
before it is declared done.

**Rationale**: An environment that works on exactly one machine is not a deployment; it
is an anecdote.

### III. Environment Parity & Portability

Local and target environments MUST run the same artifacts and the same declarative
structure. Differences between environments MUST be limited to values — never to
structure, artifact shape, or topology. Artifacts MUST NOT assume a specific provider,
cluster name, or host in a way that cannot be overridden by configuration.

**Rationale**: Parity prevents "works locally, fails elsewhere"; portability keeps the
next phase a change of values rather than a rewrite.

### IV. AI-Assisted Operations with Captured Evidence

Container and cluster operations MUST be performed with AI assistants wherever the
tooling supports it. The prompts used and the iterations taken MUST be retained as
project evidence under `history/`, because the process — not only the result — is
reviewed. AI-generated operational output MUST be confirmed by an independent,
human-observable check before it is accepted as correct.

**Rationale**: The AIOps workflow is the substance of this phase; a workflow that leaves
no trace cannot be reviewed, repeated, or improved.

### V. Security & Configuration Hygiene

Secrets MUST NEVER be committed to source, embedded in built artifacts, or written to
logs. All configuration MUST be externalized and supplied at deploy time. Every
credential MUST be replaceable without rebuilding an artifact. Workloads MUST run with
the least privilege required to function, and MUST NOT be granted cluster-wide
permissions by default.

**Rationale**: A leaked credential in a repository is unrecoverable; a rebuild-to-rotate
secret is an outage waiting to happen.

### VI. Operational Readiness

Every deployed workload MUST declare its health signal, its resource boundaries, and its
restart behavior. A workload that cannot report its own health, or that can consume
unbounded resources, is incomplete. Logs and current status MUST be obtainable without
modifying or restarting the running workload.

**Rationale**: An unobservable workload cannot be operated, only hoped for.

### VII. Verification & Evidence Discipline

No deliverable is complete until its acceptance criteria have been verified by a
reproducible command or observation, and that evidence is recorded. Claims of completion
without evidence MUST be treated as unverified. A procedure that has only been reasoned
about — never executed — does not count as verification.

**Rationale**: Reasoning produces plausible systems; execution produces working ones.

### VIII. Spec-Driven Traceability

No implementation artifact may be produced without a corresponding approved specification
and task. The hierarchy **Constitution > Specification > Plan > Tasks** governs all
conflicts. Where a requirement is missing or ambiguous, the correct action is to stop and
update the specification — never to invent behavior.

**Rationale**: Traceability is what separates spec-driven development from improvisation.

## Constitution Scope & Boundaries

### In Scope

- The principles and practices above.
- Governance: how this document is amended, versioned, and enforced.
- The definition of done for the phase, expressed as measurable outcomes.

### Out of Scope

This constitution deliberately contains **no technical specifications**. The following MUST
live in feature specifications and plans, never here:

- Languages, frameworks, libraries, runtimes, and tool selections.
- Data schemas, model definitions, and storage layouts.
- API contracts, endpoints, request/response shapes, and error taxonomies.
- Directory layouts, file names, build commands, and configuration keys.
- Performance numbers, resource sizes, and portability thresholds for specific components.

**Rule**: If a statement in this file would become obsolete after a tool upgrade, it
belongs in a spec or a plan — not in the constitution.

## Phase IV Success Criteria

Measurable outcomes that define completion of this phase. Each MUST be demonstrated with
recorded evidence.

- **SC-001**: A clean machine reaches a fully working environment by following one
  documented procedure, with no undocumented prerequisite, in under 60 minutes.
- **SC-002**: Every workload recovers to a healthy state automatically after an unplanned
  restart, with no manual intervention.
- **SC-003**: Environment differences between local and target are expressed purely as
  values; the artifact set is structurally identical.
- **SC-004**: A secret scan of the repository reports zero committed credentials.
- **SC-005**: The full acceptance suite passes from a clean environment, reproducibly,
  on two consecutive runs.
- **SC-006**: Every AI-assisted operation performed during the phase is traceable to a
  recorded prompt and iteration under `history/`.
- **SC-007**: The Phase III conversational behavior is unchanged after deployment — the
  system is re-hosted, not rebuilt.

## Governance

### Constitution Authority

This constitution supersedes all other development practices. All changes MUST comply.
Where this document conflicts with any other project artifact, this document wins.

### Amendment Procedure

1. Documented justification, including which principle is affected and why.
2. Explicit approval from the project owner.
3. Migration plan, if the amendment affects work already completed.
4. Version increment per the versioning policy below.
5. A Sync Impact Report recorded at the top of this file.

Amendments MUST NOT be made silently as a side effect of feature work. Any change to this
file is a deliberate, standalone act.

### Compliance & Review

- Every plan MUST pass a Constitution Check before design work begins, and be re-checked
  after design.
- Every review MUST verify compliance and report violations explicitly.
- Deviations MUST be recorded with justification and an accepted simpler alternative that
  was rejected, or they are not deviations — they are violations.
- Repeated violations of a principle MUST trigger an amendment discussion rather than
  quiet tolerance.

### Versioning

Semantic versioning, incremented only when this file changes:

- **MAJOR**: A principle is removed or redefined, or the constitution's scope changes
  incompatibly.
- **MINOR**: A new principle or section is added, or existing guidance is materially
  expanded.
- **PATCH**: Clarifications, wording, and typo fixes with no semantic change.

**Version**: 3.0.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-09-15
