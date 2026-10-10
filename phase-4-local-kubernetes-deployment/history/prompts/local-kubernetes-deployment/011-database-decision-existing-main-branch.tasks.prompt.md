---
id: 011
title: Database Decision - Existing Main Branch
stage: tasks
date: 2026-10-01
surface: agent
model: deepseek-v4-flash
feature: local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: none (owner decision applied to the task list)
labels: ["tasks", "t009", "database-decision", "fr-020", "deviation", "neon-mcp", "main-branch", "superseded-constraint", "never-touch-main", "flagged-decision-closed"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-local-kubernetes-deployment/tasks.md
  - history/prompts/local-kubernetes-deployment/011-database-decision-existing-main-branch.tasks.prompt.md
tests:
  - Read tasks.md T009 body (lines 143-154) before editing — the two-option block that had to become a decision record
  - grep 'DECISION REQUIRED' (run; 2 hits — line 14 the marker definition, and the T002-residue row; zero for T009)
  - grep '^\| \*\*T0' (run; flag table is now exactly 3 rows — T002 residue, T033, T025 — against a "Three tasks" intro)
  - grep '^\- \[ \] T0|^\- \[x\] T0' count (run; 58 tasks — 57 unchecked + 1 checked, unchanged by this turn)
  - grep '^```$' count (run; 2 fence lines = 1 balanced pair)
  - grep 'choice (a) or (b)|blocks T027|option (b)|if (b) was chosen|two options' (run; 1 hit initially — a stale conditional in the purge-design row — fixed; 0 remaining)
---

## Prompt

```text
use the same database branch
```

```text
use the same branch which is the main branch
```

## Response snapshot

**T009 is decided and closed: the deployment targets the existing Neon database on `main`. No `phase-iv`
branch is created, nothing is provisioned, and T009 now performs no MCP write. All six places that
described the choice as open were corrected in the same pass.**

**The decision and its honest framing.** The owner's two messages resolved the ambiguity PHR 010 flagged.
The chosen option is the one my analysis had marked as **deviating from FR-020** — FR-020 requires Phase IV
to "target a separate database or branch dedicated to this phase, so that verification runs are repeatable
and non-destructive against Phase III data", and `main` is the branch **Phase III itself uses**. So the
record is written as a **deviation, not a description of compliance**:

- The deployment reads and writes the **same dataset Phase III uses** — 104 rows across 8 tables.
- **Browser activity during T036–T049 mutates live Phase III rows.** Signing in, chatting and creating
  tasks all write to the real data. That sentence is in T009 in plain language, because it is the thing a
  reader could otherwise discover only by doing it.
- Both deployments share **one JWT keypair** in `jwks`, so a token minted by either validates against the
  other.
- **T067 must report FR-020 as NOT SATISFIED** — and T067 now says explicitly that this entry is a
  *conscious deviation* which must not be folded in with the dropped-task waivers. T008, which also
  carried an FR-020 label, was narrowed to FR-020's **direct-access clause only**, with a note that its
  green tick must not be read as FR-020 satisfied overall. FR-020 has two clauses; one holds, one does not.

**A standing constraint that no longer describes anything, retired explicitly rather than silently.** The
earlier directive — *"on the phase-iv branch only — never touch main"* — was written to scope a **purge**.
This revision withdrew the purge entirely (PHR 010: T010 dropped, T009 no longer purges), so the constraint
had been describing an operation that no longer existed while still reading like a live rule. T009 and the
Closed-since table now both say so: **read it as history, not as a live rule; the current rule is the
deviation paragraph.** That is a supersession, not a contradiction — but it needed to be written down,
because a reader who found only the old constraint would reasonably think this decision violated a standing
order.

**The ripple, again, all six sites.** Deciding T009 made six other sentences untrue — the same class of
defect as PHR 009's six stale gate references and PHR 010's FR-019 gap. Corrected together:

1. **T009 itself** — the two-option block became a decision record with the consequences and the two
   read-only steps that remain.
2. **T004's Q1 note** — "still ⚠️ DECISION REQUIRED on *which* database" → resolved to the existing
   database on `main`; Q1 no longer gates anything.
3. **Phase Dependencies** — "the one exception is T009's database choice, which blocks T027" → **Phase 1
   now gates nothing.**
4. **The Flagged Ambiguities intro and table** — T009's row removed, intro "Four tasks" → **"Three tasks"**,
   with the row count verified against the table.
5. **The Closed-since table** — Plan Q1's row rewritten from "Neon MCP server" to name the **branch
   decision**, the FR-020 deviation, and the superseded constraint.
6. **The Neon MCP appendix** — retitled from "used by T009" to **"reference only"**, since exactly **one**
   read-only tool (`get_connection_string`) remains in use. `create_branch`, `get_default_branch`,
   `update_branch` and `reset_from_parent` are now marked not-needed, and the server's destructive-tool
   notice is recorded as applying to **nothing** in this feature.

**A stale conditional found by grepping the retired option names.** A final sweep for `option (b)` /
`choice (a) or (b)` caught one surviving sentence in the purge-design row — *"if T009 option (b) is chosen,
the `phase-iv` branch inherits the parent's 104 rows…"* — still written as a hypothetical about a branch
that will never exist. Rewritten to state the settled outcome. Nothing else matched.

## Outcome

- ✅ Impact: **the last blocked decision in the task list is closed** — no task carries `DECISION
  REQUIRED` except the unrelated T002 tooling residue. The provisioning step disappeared entirely: one
  read-only MCP call remains, and **no `destructiveHint: true` tool is reachable from this feature**. The
  FR-020 deviation is now recorded in four places (T009, T008's narrowed label, the scope-revision table,
  T067's waiver list) so it cannot be quietly reported as compliance.
- 🧪 Tests: No application tests (nothing implemented, per the standing `/sp.tasks` instruction). Five
  documentary checks: `DECISION REQUIRED` occurrences, flag-row count against its intro, task count (58,
  unchanged), fence balance, and the retired-option-name grep that caught the last stale sentence. All
  ran; all clean after the fix.
- 📁 Files: `specs/004-local-kubernetes-deployment/tasks.md` (7 edits — T009, T004, T008, Phase
  Dependencies, Flagged Ambiguities intro+row, Closed-since row, scope-revision table, MCP appendix, purge
  row); this PHR.
- 🔁 Next prompts: the two remaining structural unknowns, both small: **T033** (`minikube start --ports` on
  the docker driver — decides whether the README documents a port-forward host process) and the **T002
  residue** owner call (`/sp.plan` and `/sp.phr` still write to the parent repo). Then execution can
  start at T001/T003 — **nothing gates it now.**
- 🧠 Reflection: the instruction was seven words and the work was almost entirely in the consequences. The
  owner said "the same branch which is the main branch" — a choice between two options I had written out;
  what made it a *decision* rather than a *preference* was that one option silently contradicted a
  requirement. The valuable move was not to write "✅ FR-020 satisfied" next to the chosen option, which
  would have been the frictionless thing to do and would have made the acceptance report false. The other
  half was the superseded constraint: "never touch main" was still sitting in the document, forcefully
  worded, describing a purge that had already been cancelled in the previous turn. A stale rule that
  contradicts a live decision is worse than either alone — it makes the decision look like a violation.
  Grepping the retired option names is what caught the last hypothetical.

## Evaluation notes (flywheel)

- Failure modes observed:
  1. **A cancelled operation leaving its guard behind.** "Phase-iv branch only — never touch main" was
     written for a purge; the purge was cancelled a turn earlier; the constraint stayed, still phrased as
     a prohibition. **When an operation is withdrawn, its constraints must be withdrawn with it** — a
     guard whose subject no longer exists reads as a live rule and turns a valid decision into an
     apparent violation.
  2. **A requirement with two clauses and one label.** FR-020 bundles "same provider and schema, direct
     connections" with "a separate database or branch". Three tasks wore the bare label `FR-020`;
     satisfying the first clause while deviating from the second would have shown as a green tick on a
     requirement that was not met. **Label the clause, not the requirement** — T008 now says
     "FR-020's direct-access clause only".
  3. **A decided option leaving surviving hypotheticals.** The stale "if option (b) is chosen" sentence
     was invisible to every consistency check I ran — counts, fences and row tallies all passed. It was
     found only by **grepping the names of the retired options**, which is the cheap generalizable move:
     after a choice is made, search for the option names that lost, not just for the word "decision".
- Graders run and results (PASS/FAIL): Owner-instruction conformance — **PASS** (the existing database on
  `main` is now what T009 specifies; no `phase-iv` branch anywhere as a live step). Consistency —
  **PASS** (3 flag rows vs. a "Three tasks" intro; 58 tasks; balanced fences; zero stale option
  hypotheticals after the fix). Honesty of the record — **PASS** (FR-020 reported as **deviated**, in four
  places, with the concrete consequences written out rather than softened). Non-destructiveness —
  **PASS** (document edits only; **no MCP call of any kind was made**, so nothing was created, reset or
  deleted — which is also the correct behaviour for a decision that needs no provisioning).
- Prompt variant (if applicable): n/a — owner decision applied to the task list.
- Next experiment (smallest change to try): when a task list offers a choice, immediately grep for the
  names of **both options** after the choice is made, and re-read every hit. It takes one command, it
  caught the last surviving hypothetical here, and it is the same class of sweep that found FR-019 last
  turn — the checks that catch what counts and fences cannot are the ones that search for **what changed**,
  not for **what the document says about itself**.
