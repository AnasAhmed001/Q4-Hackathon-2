---
id: 008
title: T002 Specs-Root Junction Fix
stage: misc
date: 2026-09-24
surface: agent
model: deepseek-v4-flash
feature: local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: none (owner-directed tooling fix)
labels: ["t002", "toolchain", "specify-scripts", "junction", "symlink", "collision-avoidance", "self-correction", "gitignore", "tooling-unblock"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-local-kubernetes-deployment/tasks.md
  - .gitignore (repo root, created)
  - history/prompts/local-kubernetes-deployment/008-t002-specs-root-junction-fix.misc.prompt.md
tests:
  - bash .specify/scripts/bash/check-prerequisites.sh --json (BEFORE; exit 1, "Feature directory not found: D:/My Work/Q4-Hackathon-2/specs/004-local-kubernetes-deployment")
  - bash .specify/scripts/bash/setup-plan.sh (BEFORE; exit 0 but WRONG — warned template missing, touched a phantom plan.md at the repo root)
  - MSYS=winsymlinks:nativestrict ln -s (FAILED; "Operation not permitted" — Windows Developer Mode not enabled)
  - New-Item -ItemType Junction (succeeded; LinkType=Junction, target verified)
  - junction probe: echo > specs/004-.../.junction-probe, read back from target (REAL LINK confirmed, not a copy; probe deleted)
  - diff -rq phase-3-todo-chatbot/specs/<d> phase-4-.../specs/<d> for 001-task-management-api, 001-todo-ai-chatbot, 003-frontend-todo-app (all IDENTICAL — the collision hazard is real)
  - md5sum plan.md before/after setup-plan.sh runs (16917e3832908618e96262c3685bf251 unchanged both times — touch only, no content loss)
  - check-prerequisites.sh --json / --require-tasks --include-tasks / --paths-only (AFTER; all exit 0)
  - setup-plan.sh (AFTER; exit 0)
  - git check-ignore -v specs/ (ignored via .gitignore:11); phase-4 specs NOT ignored
  - phase-1/2/3 scripts re-run (phase-1 exit 127 no bash scripts; phase-2, phase-3 exit 0 resolving to phase-4 — see correction)
  - git status (no phase-1/2/3 file modified)
---

## Prompt

```text
Fix T002 now: the .specify scripts resolve the specs root from 
`git rev-parse --show-toplevel`, which returns the parent repo root 
instead of this phase directory (phase-4-local-kubernetes-deployment/), 
so check-prerequisites.sh and setup-plan.sh both fail to find 
specs/004-local-kubernetes-deployment.

Use Option (a) from T002's own listed choices: create a symlink at the 
repo root pointing to this phase's specs/ directory, rather than making 
the phase directory its own git repo (Option b — too disruptive to other 
phases) or just documenting the workaround (Option c — doesn't actually 
fix anything).

Create the symlink, then verify:
- `bash .specify/scripts/bash/check-prerequisites.sh --json` exits 0 and 
  prints the correct absolute FEATURE_DIR
- `setup-plan.sh` does the same
- Confirm this doesn't break anything for phases 1-3's specs directories 
  if they're referenced by the same scripts

Mark T002 done only once both scripts actually pass, not just once the 
symlink exists.
```

## Response snapshot

**T002 is done and both acceptance criteria pass. The requested verification step found a real
hazard in the literal mechanism, so it was implemented in a collision-free variant — and then the
verification caught me asserting a result I had not measured.**

**Root cause confirmed by reading `common.sh`, not assumed:** `get_repo_root()` returns
`git rev-parse --show-toplevel` = `D:/My Work/Q4-Hackathon-2`; `find_feature_dir_by_prefix()` then
globs `$repo_root/specs/<prefix>-*` where `<prefix>` comes from the **branch**. So `specs/` was being
looked for at the repo root. `.specify/` itself lives inside the phase dir — the mismatch is only
that the scripts walk up to the git root.

**What was created:** a directory **junction** (not a symlink — see below) at
`Q4-Hackathon-2/specs/004-local-kubernetes-deployment` → `phase-4-local-kubernetes-deployment/specs/004-local-kubernetes-deployment`.
Native symlinking was attempted first and **failed**: `MSYS=winsymlinks:nativestrict ln -s` →
`Operation not permitted`, because Windows Developer Mode is off. A junction is the Windows-native
directory equivalent, needs no elevation, and is followed transparently by Git Bash. It was proven a
**real link, not a copy**, by writing a probe file through the link path and reading it back from the
target directory — the probe was then deleted.

**Acceptance criteria — both pass:**

| Command | Result |
|---|---|
| `check-prerequisites.sh --json` | exit **0**, `{"FEATURE_DIR":"D:/My Work/Q4-Hackathon-2/specs/004-local-kubernetes-deployment","AVAILABLE_DOCS":[]}` |
| `check-prerequisites.sh --json --require-tasks --include-tasks` | exit **0**, additionally resolves `["tasks.md"]` |
| `check-prerequisites.sh --paths-only` | exit **0**, all six paths printed |
| `setup-plan.sh` | exit **0** |

**Finding 1 — the literal instruction (link `specs/` wholesale) would have caused silent
cross-phase corruption.** `phase-4/specs/` contains byte-identical copies of `001-task-management-api`,
`001-todo-ai-chatbot` and `003-frontend-todo-app` (all three confirmed by `diff -rq`). A wholesale link
would expose those names at the repo root, so a run on a `003-*` branch would resolve
`root/specs/003-frontend-todo-app` to **this phase's copy** — converting a loud
`Feature directory not found` into a *silent* wrong-tree read, where `/sp.plan` could overwrite this
phase's files. The junction exposes only `004-*`, so those prefixes resolve to nothing. **The
deviation is the mechanism, not the goal: it is still a root-level alias, still option (a).**

**Finding 2 — my own claim, falsified by the verification the owner asked for.** I wrote that
phases 1–3's "failure behaviour is unchanged (still loud)." Measured: **phases 2 and 3 now exit 0**,
resolving to `.../specs/004-local-kubernetes-deployment`. Cause: all four phases share **one git repo
and one checked-out branch**, and the feature is derived from the **branch, not the directory** — so
every phase's copy of the scripts asks for `004-*` while the repo is on branch 004. On any other
branch they resolve `<prefix>-*`, which the junction does not expose, and fail loudly as before. No
phase-1/2/3 file is read or written (`git status` confirms none modified). Phase 1 is N/A — it ships
`.specify/scripts/powershell` only (exit 127, before and after). **Both `tasks.md` locations carrying
the wrong claim were corrected.** The practical impact is low, but the claim was false and is now
recorded accurately rather than left standing.

**Housekeeping forced by the work:** `setup-plan.sh` calls `mkdir -p "$FEATURE_DIR"` + `touch
"$IMPL_PLAN"` *before* printing, so the baseline run silently manufactured a phantom
`Q4-Hackathon-2/specs/004-local-kubernetes-deployment/plan.md` (0 bytes) at the repo root. I created it,
so I removed it before creating the junction. `plan.md`'s content hash was captured before and after —
`16917e3832908618e96262c3685bf251`, unchanged, since `touch` alters mtime only.

**Git guard:** the repo root had no `.gitignore`, so the junction showed as untracked `?? specs/` and
a `git add .` at root would have followed it and duplicated this phase's spec files into the root
tree. Created `Q4-Hackathon-2/.gitignore` with an anchored `/specs/` plus an explanatory comment.
Verified: `git check-ignore -v specs/` matches, while `phase-4-.../specs/...` is **not** ignored and
remains trackable.

**Flagged, not fixed — the same root cause has two more call-sites:** `setup-plan.sh` looks for its
template at `$REPO_ROOT/.specify/templates/plan-template.md` (and warned that it is missing), and
`create-phr.sh` looks for `phr-template.prompt.md` there *and* writes PHRs to
`$REPO_ROOT/history/prompts/`. So `/sp.plan` would `touch` an empty `plan.md` instead of copying the
template, and script-created PHRs would land outside the phase — where FR-024/SC-011 evidence is
expected. A `.specify/` and/or `history/` junction has global reach, so it needs an owner call rather
than a silent second fix. Recorded as a new Flagged Ambiguities row.

## Outcome

- ✅ Impact: T002 is closed — the two named scripts now exit 0 with the correct absolute
  `FEATURE_DIR`, verified from a clean shell from the phase root, unblocking `/sp.implement` and every
  later `/sp.*` command. A silent-corruption hazard in the literal instruction was avoided, and a
  false verification claim I had written was caught and corrected in the document.
- 🧪 Tests: No application tests (tooling fix; nothing implemented). Verification was command-level and
  is listed in the `tests:` block — including the before/after pair, the junction-realness probe, the
  three-command acceptance sweep, the `md5` integrity check on `plan.md`, and the cross-phase behaviour
  measurement.
- 📁 Files: `Q4-Hackathon-2/.gitignore` (created, anchored `/specs/`); `Q4-Hackathon-2/specs/` (created,
  contains the junction only); `specs/004-local-kubernetes-deployment/tasks.md` (T002 marked done and
  expanded; Flagged Ambiguities T002 row replaced; Closed-since row added; two false claims corrected);
  this PHR.
- 🔁 Next prompts: Owner decision on the **T002 residue** (mirror `.specify/` and `history/` at the repo
  root, or accept the degraded template/PHR paths). Then **T004** Q2/Q3, then whether to write
  `deploy/reset-db.sh` (T010). **T009 still requires its own explicit confirmation to run.**
- 🧠 Reflection: The owner asked for three verifications and every one of them produced something —
  the third produced a correction to my own work. I asserted "phases 1–3 still fail loudly" from the
  reasoning that the junction exposes only `004-*`, which is true and irrelevant: I had forgotten that
  the *branch* selects the prefix, and that one repo means one branch for all four phases. The claim
  was written before the loop that would have refuted it. This is the second time in this phase that a
  confident inference written into a document was killed by the cheap query sitting right next to it
  (PHR 005's `logical_size`). The pattern is specific and worth naming: **when a claim is about
  behaviour, the verification must run before the sentence is written, not after.**

## Evaluation notes (flywheel)

- Failure modes observed:
  1. **A behaviour claim written from reasoning instead of measurement.** "Phases 1–3 still fail
     loudly" was inferred from the junction's contents and was wrong because branch — not directory —
     drives feature resolution. Two commands would have settled it; they were run afterwards for
     exactly that reason, and they contradicted the text.
  2. **A destructive-looking side effect from a "read-only" diagnostic.** Running `setup-plan.sh` to
     capture a baseline *created* a directory and a file at the repo root (`mkdir -p` + `touch` run
     before any output). I caused it, detected it via `git status`, removed it, and hash-verified that
     the real `plan.md` was not damaged. Baseline runs of write-capable scripts are not read-only.
  3. **An instruction followed literally would have been harmful.** Option (a) as written ("a symlink at
     the repo root pointing to this phase's `specs/` directory") would have exposed `001-*`/`003-*` at
     the root. The owner's requested verification is what surfaced it; without that step the fix would
     have looked correct and passed both acceptance criteria.
  4. **Platform capability assumed rather than tested.** `ln -s` is the natural reading of "symlink";
     on this host it is unavailable without Developer Mode. The junction fallback was verified to be a
     real link, not a copy, because a silent copy would have passed the acceptance tests while going
     stale.
- Graders run and results (PASS/FAIL): Owner acceptance criteria — **PASS** (both scripts exit 0 with
  the correct absolute `FEATURE_DIR`, from a clean shell). Non-destructiveness — **PASS with one
  self-inflicted artifact** (phantom root feature dir created by the baseline run; removed; real
  `plan.md` hash-verified unchanged; no phase-1/2/3 file touched). Verification-before-writing —
  **FAIL then corrected**: a behaviour claim was written before its measurement; falsified by the
  owner-requested check and corrected in both locations. Deviation-discipline — **PASS** (mechanism
  changed from the literal instruction, with the hazard, the evidence and the reasoning all recorded in
  the task rather than applied silently).
- Prompt variant (if applicable): n/a — single owner-directed fix with explicit acceptance criteria.
- Next experiment (smallest change to try): for any claim of the form "X still behaves as before",
  run the command against X **first** and paste its output into the sentence. Both of this phase's
  falsified claims (PHR 005, PHR 008) would have been prevented by that one habit, and each cost a
  correction pass in a document that had already been written.
