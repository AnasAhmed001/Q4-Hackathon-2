---
id: 004
title: Phase IV Constitution Principles Without Tech Specs
stage: constitution
date: 2026-09-15
surface: agent
model: deepseek-v4-flash
feature: none
branch: 001-todo-ai-chatbot
user: AnasAhmed001
command: /sp.constitution i have completed phase 3 and now want to start implementing phase 4, see the @Hackathon II - Todo Spec-Driven Development.md file to see the details for phase 4, the constitution should not include technical specifications.
labels: ["constitution", "phase-iv", "kubernetes", "principles", "governance", "scope-reduction"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

i have completed phase 3 and now want to start implementing phase 4, see the @"Hackathon II - Todo Spec-Driven Development.md"  file to see the details for phase 4, the constitution should not include technical specifications.

## Response snapshot

Rewrote `.specify/memory/constitution.md` as the Phase IV constitution, v2.1.0 → **v3.0.0** (MAJOR).

The governing instruction was that the constitution must contain **no technical specifications**. The previous Phase III constitution was roughly half technology: a non-negotiable stack table, fixed database models, an API endpoint contract, code quality standards, and deployment standards. All of that was removed and relocated to specs/plans.

Replaced the five Phase III principles with eight Phase IV principles at the practice level:

I. Declarative & Version-Controlled State · II. Reproducibility from a Clean State · III. Environment Parity & Portability · IV. AI-Assisted Operations with Captured Evidence · V. Security & Configuration Hygiene · VI. Operational Readiness · VII. Verification & Evidence Discipline · VIII. Spec-Driven Traceability

Added two sections: **Constitution Scope & Boundaries**, which explicitly lists what is out of scope (languages, frameworks, schemas, API contracts, directory layouts, tool selections) and encodes the rule *"if a statement would become obsolete after a tool upgrade, it belongs in a spec or a plan"*; and **Phase IV Success Criteria** (SC-001…SC-007), stated as measurable outcomes with no technology named — clean-machine setup under 60 minutes, automatic recovery after restart, secrets scan clean, reproducible acceptance runs, AIOps prompts recorded, Phase III behavior unchanged.

Removed: Technology Stack (Non-Negotiable), Database Models (Fixed), API Endpoint, Code Quality Standards, Deployment Standards, Development Workflow. Governance was expanded — amendments must be standalone and never a side effect of feature work; repeated violations trigger an amendment discussion rather than quiet tolerance; MAJOR now explicitly covers a change in the constitution's scope.

Consistency propagation: plan-template.md, spec-template.md, and tasks-template.md were read and need **no edits** — the Constitution Check in plan-template is generic and defers to this file, and the other two have no constitution coupling. `.specify/templates/commands/` does not exist in this repo; the equivalent command files under `.claude/commands/` and `.opencode/commands/` were reviewed and contain no principle-specific references. Sync Impact Report prepended as an HTML comment.

## Outcome

- ✅ Impact: Constitution scope narrowed to principles and governance only; all technical content relocated to specs/plans. Phase IV principles now describe deployment practice (declarative, reproducible, parity, AIOps-evidenced, secure, observable, verified, traceable) without naming a single tool.
- 🧪 Tests: none (documentation artifact)
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: `/sp.specify` for the Phase IV local Kubernetes deployment feature, then `/sp.plan` (its Constitution Check must be run against the new eight principles) and `/sp.tasks`
- 🧠 Reflection: The "no technical specifications" constraint is what drove the MAJOR bump rather than a MINOR one — removing normative sections changes what the document governs, not just what it says. Encoding that boundary as an explicit Out-of-Scope rule (rather than relying on future authors to infer it) is what keeps the constitution from drifting back toward a stack list. Two principles carry the phase's real risk: IV (AIOps evidence must be retained under `history/`, since the workflow itself is graded) and III (parity now, so Phase V cloud deployment is a change of values, not a rewrite).

## Evaluation notes (flywheel)

- Failure modes observed: `.specify/scripts/bash/create-phr.sh` failed with "PHR template not found at .specify/templates/ or templates/" although `.specify/templates/phr-template.prompt.md` exists — the script's expected filename differs. Fell back to agent-native creation per CLAUDE.md step 5 and wrote the file directly from the template.
- Graders run and results (PASS/FAIL): PASS — no unresolved placeholders; version line 3.0.0 matches the Sync Impact Report; dates in ISO format; principles are declarative and use MUST rather than "should"; path is under `history/prompts/constitution/` and matches stage.
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Inspect `create-phr.sh` for the template filename it expects and reconcile it with `.specify/templates/phr-template.prompt.md` so the shell path works on the next run.
