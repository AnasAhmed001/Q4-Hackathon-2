---
id: 005
title: Phase IV Parent Branch Row-Count Probe
stage: misc
date: 2026-09-24
surface: agent
model: deepseek-v4-flash
feature: local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: none (direct request for measurement)
labels: ["neon-mcp", "run-sql", "phase-iv", "t009", "fr-020", "sc-005", "evidence-capture", "premise-falsified", "jwks", "data-isolation"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/local-kubernetes-deployment/005-phase-iv-parent-branch-row-count-probe.misc.prompt.md
  - history/prompts/local-kubernetes-deployment/004-neon-mcp-access-verification.misc.prompt.md (corrected)
tests:
  - get_default_branch(project_id="billowing-wind-59531724") (run; current_state now "ready", state_changed_at 2026-09-24T17:25:25Z — the archived blocker from PHR 004 is CLEARED)
  - run_sql "information_schema.tables" (run; 9 tables in public)
  - run_sql "count(*) union over 8 tables" (run; 104 rows total — premise falsified)
  - run_sql "min/max created_at per table" (run; FAILED first attempt, see failure modes)
  - run_sql "information_schema.columns" (run; resolved the camelCase/snake_case split)
  - run_sql "SELECT ... FROM \"user\"" (run; 4 accounts, all @gmail.com, all emailVerified=false)
  - run_sql "SELECT version_num FROM alembic_version" (run; 20260206_01)
  - run_sql "pg_total_relation_size per table" (run; all 9 tables = 488 kB combined)
  - run_sql "pg_database_size" (run; neondb = 7,968 kB, 7,480 kB unattributed)
---

## Prompt

```text
main is no longer archived — I woke it up by querying the app directly. 
Please now run the row-count probe: get_default_branch to confirm main's 
current state is ready, then run_sql SELECT count(*) on the task and 
session/user tables. I need the real numbers before deciding how T009 
handles the clone.
```

## Response snapshot

**`main` is `ready`** — `state_changed_at: 2026-09-24T17:25:25Z`. The PHR 004 blocker is cleared. The
parent branch is now a valid copy-on-write source for T009.

**Row counts on `main` (neondb, branch `br-snowy-surf-ahjdfzub`) — the premise is FALSIFIED:**

| table | rows | size |
|---|---|---|
| `message` | **64** | 120 kB |
| `conversation` | **17** | 48 kB |
| `task` | **9** | 64 kB |
| `session` | **5** | 80 kB |
| `account` | **4** | 48 kB |
| `user` | **4** | 48 kB |
| `jwks` | **1** | 32 kB |
| `verification` | 0 | 24 kB |
| `alembic_version` | 1 | 24 kB |
| **total** | **105** | **488 kB** |

`plan.md` asserts the parent branch holds *"zero rows of Phase III production data."* It holds **104 data
rows across 8 tables.** The premise is false, and T009's step 5 `run_sql` check — written as a
confirmation step — has now failed in advance. Migration head is `20260206_01`.

**The data is stale Phase III-era demo/test content, not live traffic.** Newest row anywhere is
2026-03-29; today is 2026-09-24, so it has been dormant ~7 months.

| table | oldest | newest |
|---|---|---|
| `user` | 2026-01-14 | 2026-02-05 |
| `task` | 2026-01-15 | 2026-02-13 |
| `conversation` | 2026-02-08 | 2026-02-13 |
| `session` | 2026-01-16 | 2026-03-29 |

Contents: 4 users, all `@gmail.com`, all `emailVerified: false` — `anas@gmail.com` ("Anas Ahmed",
2026-01-14), `uzair@gmail.com` ("Anas Ahmed", 2026-01-14), `uz@gmail.com` ("Barat", 2026-01-16),
`new@gmail.com` ("new user", 2026-02-05). The last one is unambiguously a test fixture. 4 `account` rows
carry `password` hashes.

**CORRECTION to PHR 004 — the 30 MB figure was a red herring.** The entire database is
**7,968 kB (7.8 MB)**; all nine tables together are **488 kB**; 7,480 kB is unattributed (catalog,
TOAST, free space). Neon's `logical_size` (31,588,352 B) is a **billing metric**, reporting ~4× the real
`pg_database_size`. PHR 004's inference — "≈30 MB, therefore substantial row data" — was **wrong**, and
004 now carries a correction note. The row counts above were the only valid evidence; a metadata field
was never a proxy for table contents.

**Two schema conventions coexist in `public`** — relevant to any purge script T010 might carry:
- **Backend / Alembic** (`snake_case`): `task`, `conversation`, `message` — `created_at`, `user_id`
- **Better Auth / frontend** (`camelCase`, quoted): `user`, `session`, `account`, `verification`, `jwks` —
  `"createdAt"`, `"userId"`

A naive `DELETE` script written in one convention silently fails on the other half.

**Two clone hazards the row counts expose, both security-relevant for FR-020:**

1. **`jwks` (1 row)** holds a JWT **signing keypair** (`publicKey`/`privateKey`). Better Auth signs
   session tokens with it; the backend validates via JWKS. A clone inherits the **same keypair**, so a
   token minted by the Phase III deployment validates against the Phase IV backend and vice versa. That
   is a cross-environment trust leak, not merely stale data.
2. **`session` (5 rows)** holds live session `token` values. Cloned into `phase-iv`, those tokens remain
   valid credentials there. Combined with `account.password` hashes, the clone carries real
   credential material.

**No writes were performed.** All calls were read-only `SELECT`/metadata. No branch created, no `DELETE`,
no `TRUNCATE`. Purging would be destructive SQL, which the MCP requires explicit approval for.

## Outcome

- ✅ Impact: T009's central premise is **disproven by measurement**, and the owner now has the real
  numbers requested instead of an estimate. The archived-branch blocker is cleared. The clone decision
  is reframed: the question is no longer "is the parent clean?" (it is not) but "what does T009 do about
  the 104 inherited rows and the inherited signing key?" The `jwks` finding is the one that makes plain
  cloning unsafe even for a throwaway environment.
- 🧪 Tests: Nine read-only MCP calls; one failed and was corrected (below). No application tests. Zero
  writes; no destruct`ve tool touched.
- 📁 Files: This PHR; PHR 004 corrected with a falsified-inference note. **`tasks.md` deliberately
  untouched** — the owner said they need the numbers *before* deciding how T009 handles the clone, so
  rewriting T009 now would pre-empt that decision.
- 🔁 Next prompts: Owner decides among the clone strategies below; then T009/T010 are re-rendered to
  match. Still open from PHR 003: **T002** (`.specify` specs-root mismatch, blocks `/sp.implement`) and
  **T004** Q2/Q3.
- 🧠 Reflection: Two metadata reads produced a confident wrong answer; two SQL counts produced the right
  one. The specific trap — treating Neon's `logical_size` as evidence about row data — is worth naming
  because it is invisible: the number was real, the field was real, only the *inference* was fabricated.
  Notably, my own T009 text had already flagged the "zero rows" premise as resting on faith and
  prescribed the exact query that would settle it; running it was always the cheap move, and deferring it
  to implementation time is what let a false premise survive to a 68-task plan.

## Clone strategies for T009 — options, not a decision

Presented because the owner asked for numbers *in order to* decide; no option is applied.

| | Approach | Consequence |
|---|---|---|
| **A** | Clone `main` → purge all 8 data tables **including `jwks`** | Schema + `20260206_01` head guaranteed; `jwks` purge forces Better Auth to mint a fresh keypair, restoring token isolation. Needs approved destructive SQL; must handle both naming conventions. |
| **B** | Clone `main`, then `reset_from_parent` for clean state | **Does not work** — the parent *is* the data source, so every reset re-imports all 104 rows. Confirms PHR 003's flagged reset-semantics hazard as a real defect, not hypothetical. |
| **C** | Clone `main` and accept the inherited data | Fails FR-020's isolation reading and SC-005's "verifiable as empty" gate. Cloned session tokens stay valid. |
| **D** | Schema-only branch | **Not available** — MCP `create_branch` has no schema-only mode (`init_source: "parent-data"`), and no snapshot predates the data (project created 2026-01-13, first user 2026-01-14). Degenerates to A. |

Also refined: T009's TTL hazard came from `neon.ts`, which is the **app's** Neon integration
(`neon checkout`), **not** the MCP path — MCP `create_branch` exposes no `expires_at` parameter. The
verification step stays (via `update_branch`'s `expires_at`), but it is lower-risk than T009 implies.

## Evaluation notes (flywheel)

- Failure modes observed:
  1. **Platform metadata treated as a proxy for row data.** `logical_size` (a billing metric, 30 MB) was
     reasoned from as if it measured table contents. Real database: 7.8 MB; real tables: 0.5 MB. The
     inference was wrong in the *upward* direction and made the data look 60× larger than it is.
  2. **`SELECT ... FROM "user"` failed on `created_at does not exist`** — Better Auth uses camelCase
     quoted identifiers. Rather than guess again, the fix was to read `information_schema.columns`
     first. Two calls were wasted on guessed column names before that.
  3. **A false premise survived from `plan.md` through a 68-task breakdown** and was only killed by a
     direct query. T009 had flagged it as unverified and named the detector — proof that flagging is not
     the same as verifying, and that a named-but-unrun check is still an unrun check.
  4. **A `UNION ALL` across mixed schemas fails wholesale** — one bad table name in the union nulled the
     entire result rather than returning partial data, hiding three good answers behind one bad one.
- Graders run and results (PASS/FAIL): Non-destructiveness grader — **PASS** (zero writes; every call a
  `SELECT` or metadata read). Evidence-capture grader — **PASS** (all outputs recorded under `history/`
  per FR-024/SC-011). Self-correction grader — **PASS** (PHR 004's falsified inference corrected in
  place, with the reasoning error named rather than quietly edited out). Decision-discipline grader —
  **PASS** (four strategies laid out, none applied; `tasks.md` left untouched pending the owner's call).
- Prompt variant (if applicable): n/a — single direct measurement request.
- Next experiment (smallest change to try): Make the first action of any infrastructure-facing task a
  **`count(*)`-class query against the resource itself**, never a metadata field — one call, and it
  would have replaced both the wrong 30 MB inference and the "zero rows" premise with the actual number
  before either reached a document.
