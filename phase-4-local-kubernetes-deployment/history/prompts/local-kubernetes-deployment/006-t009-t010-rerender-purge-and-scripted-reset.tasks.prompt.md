---
id: 006
title: T009/T010 Re-render with Purge and Scripted Reset
stage: tasks
date: 2026-09-24
surface: agent
model: deepseek-v4-flash
feature: local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: none (owner decision applied to tasks)
labels: ["tasks", "t009", "t010", "neon-mcp", "truncate", "sc-005", "fr-020", "jwks", "branch-guard", "flagged-deviation"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-local-kubernetes-deployment/tasks.md
  - history/prompts/local-kubernetes-deployment/006-t009-t010-rerender-purge-and-scripted-reset.tasks.prompt.md
tests:
  - run_sql pg_constraint (run; FK graph = account→user, session→user, task→user, message→conversation, all ON DELETE CASCADE)
  - run_sql pg_settings LIKE 'neon%' (run; discovered neon.branch_id = br-snowy-surf-ahjdfzub — the T010 branch guard)
  - Read backend-api/src/auth/jwt_validator.py (read; found the module-level PyJWKClient singleton + 300s cache that rules out per-reset jwks purging)
  - grep task count (run; 68 tasks T001-T068, no gaps)
  - grep Done-when count (run; 69 matches = 68 task lines + 1 format-description line at :54; no defect)
  - grep stale mechanism claims (run; none — "MCP reset", "no TRUNCATE script" all removed)
  - grep fence balance (run; 8 fences, EVEN)
  - sed compare of both TRUNCATE statements (run; T009 = 8 tables incl. jwks, T010 = 7 tables excl. jwks — correct)
---

## Prompt

```text
Going with Option A: clone main, then purge all 9 tables (task, 
conversation, message, session, account, user, jwks, verification, 
alembic_version) on the phase-iv branch only — never touch main.

Handle both naming conventions correctly: backend tables (task, 
conversation, message) use snake_case; Better Auth tables (user, session, 
account, jwks, verification) use quoted camelCase. Verify against 
information_schema.columns per table before writing the purge, not after.

Purging jwks is required, not optional — it forces a fresh signing keypair 
on the phase-iv branch, closing the cross-environment token validity issue 
you found. Do not preserve or copy the existing keypair.

Keep alembic_version — that's schema version tracking, not application 
data; purging it would make T009's "confirm migration head" check fail 
for the wrong reason.

Re-render T009 to add this purge as an explicit step after create_branch 
and before the zero-row verification, and T010's reset flow (or the reset 
detector) should account for the fact that the parent will re-introduce 
this data on every reset_from_parent call — flag whether that changes the 
recommended reset approach.

I want the reset step in the automated deploy/verification loop, not a 
manual confirmation each time. Here's how to structure it:

1. T009 (branch creation + JWKS purge) is a ONE-TIME setup act, done once 
with my explicit confirmation, exactly as planned. It never runs again 
as part of the repeatable procedure — don't design it to be re-run.

2. Replace T010's reset mechanism entirely. Do NOT use reset_from_parent 
(confirmed broken — it re-imports main's data every time, and it's a 
destructiveHint tool the MCP server refuses to run unattended anyway).

3. Instead, write deploy/reset-db.sh as a plain SQL script that connects 
directly to the phase-iv branch (via psql or asyncpg using the stored 
DATABASE_URL) and TRUNCATEs the same 9 tables from T009's purge — 
respecting the snake_case/camelCase split you already identified. This 
is a normal database script, not an MCP tool call, so it can run fully 
unattended as part of deploy.sh / the verification loop with no 
confirmation gate.

4. This script becomes the canonical SC-005 reset mechanism for both 
T065 and T066 — fast, no MCP dependency at reset time, and it can't 
re-introduce Phase III data since it never touches main.

Re-render T009 and T010 to reflect this split: T009 stays a one-time 
manual-confirmation setup task; T010 becomes a fully scripted, automatable 
TRUNCATE that needs no per-run approval.
```

## Response snapshot

**T009 and T010 re-rendered, plus 6 consistency edits to remove every stale reference to the old
mechanism.** `tasks.md` remains 68 tasks, T001–T068, no gaps, all fences balanced.

**T009 is now `🔐 ONE-TIME SETUP, requiring explicit owner confirmation`,** explicitly marked
non-re-runnable ("do not design this task to be re-run"). Steps: `get_default_branch` (+ **assert
`current_state == "ready"`** — `main` was observed archived and had to be woken) → `create_branch` →
`get_branch`/`update_branch` TTL check → `get_connection_string` → **🔴 PURGE (step 5)** → zero-row
verification (step 6) → `describe_branch` (step 7). The purge documents the 8-table/per-convention
inventory with the column list verified against `information_schema.columns`, the exact `TRUNCATE`
statement, and the verified FK graph.

**T010 is now `deploy/reset-db.sh` — scripted, fully unattended, no confirmation gate**, with
`reset_from_parent` explicitly retired and recorded as rejected so it is not re-litigated.

**Mandatory pre-write verification the owner asked for — all done before writing, not after:**

| Check | Method | Result |
|---|---|---|
| Per-table columns + convention | `information_schema.columns` (read in the prior turn) | 3 snake_case tables, 5 camelCase; `"user"` is a reserved word and needs quoting |
| FK graph | `pg_constraint` | `account`/`session`/`task` → `"user"`, `message` → `conversation`, all `ON DELETE CASCADE`. **Every parent is inside the purge set → plain `TRUNCATE`, no `CASCADE`** |
| Branch-identity enforcement | `pg_settings LIKE 'neon%'` | **`neon.branch_id` is a real runtime GUC** — the `main` connection reports `br-snowy-surf-ahjdfzub` |
| Whether per-reset `jwks` purge is safe | `backend-api/src/auth/jwt_validator.py:62-70` | **Not safe** — module-level `PyJWKClient` singleton, `cache_keys=True`, PyJWT default 300 s `cache_jwk_set` lifespan |

**Two deliberate deviations from the prompt, both flagged in the document rather than silently applied:**

1. **Table count — the prompt said "all 9 tables" and listed `alembic_version`, then said to keep it.**
   Those two instructions conflict. The reasoned one wins: **8 tables are purged in T009**, `alembic_version`
   retained. T010's "same 9 tables" is likewise **7 tables**. Both counts are now stated explicitly with the
   reasoning, so the arithmetic is checkable rather than inherited.
2. **`jwks` is purged in T009 but NOT in T010's per-run reset.** This is the answer to the owner's question
   *"flag whether that changes the recommended reset approach"* — it does, and for a reason that did not
   exist until `jwt_validator.py` was read. Truncating `jwks` mid-run leaves the running backend verifying
   against its cached JWK set while the frontend signs with a different key, producing **401s for up to
   300 s**. Since the `jwks` purge is only needed *once* (to destroy the keypair inherited from `main`), and
   T009 runs before any pod exists, the purge is safe exactly once and harmful on repeat. A signing key is
   infrastructure, not application state — the same category as `alembic_version`.

**The branch guard is stronger than requested.** Rather than a string test on `NEON_BRANCH`, T010 asserts on
the connection itself: `current_setting('neon.branch_id')` must equal `phase-iv`'s id and
`current_setting('neon.project_id')` must equal `billowing-wind-59531724`, else exit non-zero having written
nothing. This reads the branch the connection is **actually attached to**, so a misconfigured
`DATABASE_URL` — the realistic way Phase III data gets destroyed — cannot defeat it. T010 also requires
testing the guard *by pointing it at `main`*, since that is its only real proof.

**Consistency edits (6)**: `T004`'s stale "provisioned and reset through the Neon MCP server … no TRUNCATE
script" line; the critical-path diagram's `T010 (MCP reset)`; the MVP-strategy line claiming
`T009/T010/T041/T064` all gate on `T004`; T065's and T066's "T010 branch reset" phrasing; and the
"Neon MCP tool contracts" section — retitled to T009 only, with `reset_from_parent` marked `⛔ NOT USED` and
the verified `neon.*` GUCs added as a new contract table.

## Outcome

- ✅ Impact: The T009/T010 split the owner specified is implemented in full — one-time confirmed setup
  versus unattended repeatable reset — with a reset that needs **no MCP access at all**, so SC-005's two
  consecutive runs are automatable. Two deviations are flagged rather than absorbed, and both are
  technically forced by evidence gathered this turn (a conflicting instruction; a 300 s auth-cache
  failure mode). The "never touch `main`" constraint is now enforced at the connection level rather than by
  operator discipline.
- 🧪 Tests: No application tests (nothing implemented — no application code written, per the standing
  `/sp.tasks` instruction). Validation was structural and mechanical: 68 tasks, sequential IDs, no gaps,
  68 task `Done-when` lines (a 69th grep hit at `:54` is the format description, not a task), 8 balanced
  fences, no stale mechanism claims, and the two `TRUNCATE` statements diffed to confirm 8-vs-7 tables.
- 📁 Files: `specs/004-local-kubernetes-deployment/tasks.md` (T009, T010 re-rendered; 6 consistency
  edits); this PHR.
- 🔁 Next prompts: `deploy/reset-db.sh` itself is **not written** — that is T010's implementation step, and
  the standing `/sp.tasks` instruction is "do not write implementation code yet." **Owner may say the word
  to create it now**; note it cannot be *tested* until T009 has run, since it needs `PHASE_IV_DATABASE_URL`
  and the `phase-iv` branch id. Still open: **T002** (`.specify` specs-root mismatch, blocks
  `/sp.implement`) and **T004** Q2/Q3.
- 🧠 Reflection: The owner's instruction contained an internal contradiction (purge all 9 tables incl.
  `alembic_version` / keep `alembic_version`) and the correct move was to apply the reasoned half and
  **name the discrepancy** rather than silently pick one — an unflagged silent choice here would have made
  the task list look conformant while quietly disagreeing with the person who wrote it. Separately, the
  `jwks` question is the clearest case so far of reading source *before* writing the plan: the instruction
  "purging jwks is required" was correct for T009 and would have been a defect in T010, and nothing but
  `jwt_validator.py:62-70` could have revealed the difference.

## Evaluation notes (flywheel)

- Failure modes observed:
  1. **An instruction pair that cannot both hold** — "purge all 9 tables (…, alembic_version)" alongside
     "keep alembic_version." Resolved by preferring the specific, reasoned instruction and documenting the
     delta. Worth a general rule: when a prompt's enumeration and its explicit exclusion disagree, the
     exclusion usually carries the intent, and the count is usually stale bookkeeping carried over from
     the assistant's own prior message — which is exactly what happened here (my "nine tables" list
     included `alembic_version`).
  2. **A mechanism correct at one call-site and wrong at another.** `jwks` purging is required once and
     harmful on repeat. The owner's instruction was not wrong; it was under-scoped, and only source
     reading distinguished the two cases.
  3. **Inherited stale cross-references after a mechanism swap.** Re-rendering T009/T010 left five other
     places asserting the old mechanism (T004's Q1 note, the critical-path diagram, the MVP strategy, T065,
     T066). Found only by grepping for the retired name after editing — a re-render is not finished when
     the target blocks are correct, but when nothing else contradicts them.
- Graders run and results (PASS/FAIL): Owner-instruction conformance — **PASS with 2 flagged deviations**
  (both documented in-task and in the Flagged Ambiguities table, neither silent). Non-destructiveness —
  **PASS** (this turn made zero MCP writes; every call was `SELECT`/metadata). Verification-before-writing
  — **PASS** (columns, FKs, and the GUC were all established before the purge text was composed).
  Consistency — **PASS** (zero stale mechanism claims remain). Format — **PASS** (68 tasks, sequential,
  fences balanced, Done-when per task).
- Prompt variant (if applicable): n/a — single owner decision applied to the task list.
- Next experiment (smallest change to try): When a mechanism is retired, grep for its **name** across the
  whole document immediately after the swap and treat every hit as a required edit. Five of this turn's six
  consistency edits came from that single grep, and none would have been caught by re-reading the edited
  blocks.
