---
id: 010
title: Q2/Q3 Corrections and Hackathon Scope Reduction
stage: tasks
date: 2026-10-01
surface: agent
model: deepseek-v4-flash
feature: local-kubernetes-deployment
branch: 004-local-kubernetes-deployment
user: AnasAhmed001
command: none (owner corrections and scope reduction applied to the task list)
labels: ["tasks", "correction", "falsified-claim", "scope-reduction", "q2", "q3", "t041", "t064", "t058", "t009", "t005", "t030", "t048", "fr-019", "fr-020", "fr-027", "sc-004", "sc-005", "hackathon-scope", "no-new-tool-installs"]
links:
  spec: specs/004-local-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-local-kubernetes-deployment/tasks.md
  - backend-api/.env.example
  - history/prompts/local-kubernetes-deployment/009-q2-q3-decisions-closed-connection-budget-and-trufflehog.tasks.prompt.md
  - history/prompts/local-kubernetes-deployment/010-q2-q3-corrections-and-scope-reduction.tasks.prompt.md
tests:
  - Read backend-api/.env.example (21 lines; found a live-looking Neon DATABASE_URL password and GEMINI_API_KEY on disk — the file to sanitize)
  - git check-ignore -v backend-api/.env.example + git ls-files (FOUND: untracked AND gitignored via backend-api/.gitignore:15 — the credentials were never committed; only on disk)
  - grep FR/SC sets from spec.md vs tasks.md (comm -23 both directions — initially FR-019 unreferenced anywhere; closed by assigning it to T048)
  - grep -o 'T0[0-9][0-9]' defined-vs-referenced diff (8 referenced-but-undefined IDs; all 8 are dropped IDs and every reference sits in the scope-revision drop table or an explicit "was dropped" clause)
  - grep -c '^- \[ \] T0' + '^- \[x\] T0' (run; 57 + 1 = 58 tasks — 68 minus the 10 dropped, IDs kept stable, none renumbered)
  - grep 'carry a decision' + awk row count (run; intro says "Four tasks", table has exactly 4 rows)
  - grep -n '```' (run; 2 fence lines = 1 balanced pair, the critical-path diagram)
  - grep -in 'trufflehog|gitleaks|docker scout' (run; 4 hits, all in rejection/correction contexts — no selection survives)
  - grep -in 'pooled|~112|ceiling 12|9×' (run; 2 hits, both correction text; T041 body is clean)
---

## Prompt

```text
[Part 1 — corrections on the Q2/Q3 closure]

1. The 901 came from me running SHOW max_connections directly in the Neon SQL
Editor. It is the direct Postgres limit for my compute, not a pooled-only number.
Remove the "901 is the pooled limit" warning and the "direct would be ~112,
ceiling 12" claim from T041, and remove the pooled-vs-direct ADR candidate from
the T068 list. Keep -pooler as the default endpoint, but do not claim a 9x swing.

2. The connection-budget maximum should not be 100. The real ceiling is the
Minikube node: each backend pod requests 100m CPU and 256Mi memory. Base T041's
stated maximum on Minikube's allocated CPU and memory (state the allocation used
when starting the cluster), and keep the 8*B + 10*F <= 901 check as a secondary
footnote only.

3. SC-004 scanner: I do not want to install TruffleHog or any new tool. Rewrite
T064 to use no new installs: grep the exported images (docker save) and
git-tracked files and history (git grep, git log -p) for my actual secret values
and common credential patterns. Remove TruffleHog as the selected scanner and
update the README/T058 requirements to match.

Update every cross-reference these changes make stale.

[Request interrupted by user]

[Part 2 — scope reduction]

This is a hackathon learning project with a handful of test users, not a
production app. Simplify tasks.md. Do not add anything new.

Keep: frontend Dockerfile and .dockerignore (T011-T013), backend image, the Helm
chart (T014-T023), the two required source changes (T024, T025), secrets wiring
(T026-T027), build/load/install (T030-T035), the browser checks (T036-T038), and
quick demos of self-healing (delete a pod) and scaling (1 to 3 replicas). Keep
the README (T058) and the history/ records.

Drop or mark optional: the collision pre-flight (T028/T029), branch reset script
and guard (T010), connection-budget math (T041), credential scanner (T064),
values-only render check (T057), regression diff (T062), contracts/data-model/
quickstart docs (T059-T061), ADR (T068), and the two audited clean-state runs
(replace with one clean run from minikube delete).

Database: no purge or reset script. Use [existing database as-is / one manually
created phase-iv branch, my choice below].

Security: after building, just confirm no .env file is inside either image and
git status shows no secrets tracked.

Fix T002 with the symlink, use Bash for the scripts, and sanitize
backend-api/.env.example to placeholders. Update cross-references and the flag
table so nothing points at dropped tasks.

SC-004 scanner: I do not want to install TruffleHog or any new tool. Rewrite T064
to use no new installs: grep the exported images (docker save) and git-tracked
files and history (git grep, git log -p) for my actual secret values and common
credential patterns. Remove TruffleHog as the selected scanner and update the
README/T058 requirements to match.
```

## Response snapshot

**`tasks.md` was rewritten from 68 tasks to 58, the falsified Q2 finding was removed, T064 was rewritten
to require no installs, and two genuine gaps surfaced by the rewrite were closed. Two items were flagged
rather than guessed.**

**A falsified claim of mine, removed.** In PHR 009 I inferred that 901 was the *pooled* ceiling, deduced
the direct endpoint would govern at ~112, and wrote that as a 🔴 "9× error latent" warning plus an ADR
candidate. The owner: the 901 came from `SHOW max_connections` run in the SQL Editor — **it is the direct
limit**. The warning and the ~112/ceiling-12 arithmetic are gone from T041, and the ADR candidate is gone
from T068's list. `-pooler` stays the default endpoint but no swing is claimed. **PHR 009's Reflection
section praised exactly the reasoning that was wrong** — it is corrected rather than quietly deleted, since
the instructive part (that I turned a blocked probe into a confident written claim) is the real lesson.

**The stated maximum was rebased on the actual constraint.** 100 was derived from the connection limit
with a 10% reserve I invented. The node is the binding constraint on a laptop: each backend pod requests
`100m`/`256Mi` (requests, not limits — that is what the scheduler uses), so T041 now derives the maximum
from `kubectl get node minikube -o jsonpath='{.status.allocatable}'` at the stated `minikube start`
allocation. **Memory binds roughly 10× sooner than CPU**, so the stated maximum is a memory number. The
90-minute-connection budget survives as a **footnote only** (`B ≤ 111` at `F=1`), explicitly marked
non-binding. A worked example at `--cpus=4 --memory=4096` gives ≈13 backends, written as arithmetic to be
**replaced by the measured value on the day**, never carried forward as a result.

**T064 rewritten to zero installs.** TruffleHog — which PHR 009 had *selected* and made an install step
for — is now explicitly rejected, along with gitleaks and `docker scout`. The scan uses `git grep` /
`git log -p` / `git log -S'<value>'` for tracked files and history, and `docker save` → `tar -xf` → `grep`
for both images, searching for **the project's actual values** (`grep -F`, since they contain regex
metacharacters) as well as generic shapes. It carries the **gzipped-layer false-negative warning**: if the
OCI layers come out compressed, a plain `grep` reports *clean* on a blob it never read — the exact failure
that would make this task certify nothing. The owner's direct check is step 4: no `.env` inside either
image, and `git status` showing nothing secret tracked.

**Scope cut to 58 tasks with IDs held stable.** T010, T028, T029, T057, T059–T062, T066 and T068 are
dropped; nothing was renumbered, so every surviving cross-reference stays valid. US1–US4 are intact and
the MVP path (T030–T041) is untouched. **Two instruction-level tensions were resolved by keeping, not
deleting, and are flagged for the owner**:

- **"Drop T041" vs. correction #2 specifying what T041 should become.** Read literally, both cannot hold.
  T041 is kept in **simplified form** — FR-027 still requires a stated maximum, and a one-paragraph
  node-derived answer is cheaper than an unsupported claim. The connection math is what got demoted.
- **Same for T064.** It is named in the drop list, and the no-install rewrite is repeated verbatim at the
  end of the message. Kept as the zero-install version, since SC-004 still needs a scan.

**The database instruction is genuinely unresolved and was not guessed.** The owner wrote *"Use [existing
database as-is / one manually created phase-iv branch, my choice below]"* — **there is no "choice below"
in the message.** T009 presents both options with their consequences and a `⚠️ DECISION REQUIRED` header.

**A spec constraint the instruction did not mention, found by re-reading the spec.** **FR-020 requires a
"separate database or branch dedicated to this phase."** That means option (a) — existing database as-is —
**is not a free pick; it is a recorded spec deviation**, and T067 must report FR-020 as **not satisfied**
if it is chosen. T009 now says so on both option lines. The owner can still take (a) deliberately; they are
no longer choosing it blind.

**Two coverage gaps closed.** A `comm -23` of the spec's FR/SC sets against the task list found
**FR-019 ("per-user data isolation and the existing authorization behavior MUST be preserved unchanged")
referenced nowhere in the document** — not verified, not waived. It is now assigned to **T048**, the
multi-replica correctness task, because replication is precisely what threatens per-user isolation: if any
user-scoped state lived in process rather than in the database, two pods would leak across each other, and
that is the only task that would catch it. All 28 FRs and 11 SCs now resolve.

**One cross-reference was left deliberately stale-looking.** The scope-revision table at the top of the
document names all ten dropped IDs with a one-line reason each, and T067's waiver list repeats FR-018,
FR-023, FR-028 and SC-005's second run — because `comm` proved those FRs are referenced *only* by their
waivers, and a reader must be able to see that they are waived rather than believe them covered.

**Also landed**: T005 rewritten (the file is **untracked and gitignored**, so its credentials were never
committed — rotation is now the owner's judgement call, not a task dependency); T030 resolved to **Bash**
(plan Q10); T002 recorded as already fixed via the **junction** (re-verified live: `LinkType = Junction`,
target intact).

## Outcome

- ✅ Impact: the document no longer contains a falsified connection-limit finding or a replica maximum
  derived from the wrong constraint. FR-027 now has a maximum anyone can reproduce from one `kubectl`
  command. SC-004 is provable with tools already on the host — **the "install a scanner" step is gone from
  the clean-machine procedure**. The task count dropped 68 → 58 with IDs stable. **FR-019 went from
  unverified-and-unmentioned to assigned**, and FR-020's "dedicated branch" requirement is now visible at
  the point of decision rather than buried in the spec.
- 🧪 Tests: No application tests — nothing implemented, per the standing `/sp.tasks` instruction, and no
  application code was written. Verification was documentary and structural: the FR/SC `comm` diff in both
  directions, the defined-vs-referenced task-ID diff, the flag-intro-vs-row count, fence balance, and two
  targeted greps proving no TruffleHog selection and no pooled-limit arithmetic survive. The one
  filesystem check was `git check-ignore` + `git ls-files` on `.env.example`.
- 📁 Files: `specs/004-local-kubernetes-deployment/tasks.md` (full rewrite); `backend-api/.env.example`
  (sanitized to placeholders); PHR 009 (correction banner); this PHR.
- 🔁 Next prompts: **T009's database choice is the only thing blocking execution** — option (a) or (b), and
  the FR-020 consequence is now written down. Then the two flagged structural items: whether `minikube
  start --ports` works on the docker driver here (T033 — the fallback changes the README), and the T002
  residue owner call (mirror `.specify/` and `history/` at the repo root, or leave `/sp.plan` and
  `/sp.phr` writing outside the phase).
- 🧠 Reflection: The instruction supplied 901 as a fact and I got the *scope* of that fact wrong — but the
  deeper error was that I had already been refused the probe that would have settled it, and I wrote the
  inference into the document anyway as a bolded finding with an ADR attached. A blocked probe is a reason
  to write a question, never a licence to write an answer. The second-order lesson from the same turn: the
  scope reduction asked me to "drop T041 and T064" while the corrections told me what those two tasks
  should *become*. Taking either instruction alone would have been wrong — dropping them loses FR-027 and
  SC-004 coverage, and keeping them as-was ignores the simplification. The resolution is to read the two
  instructions as one intent (simplify, don't delete) **and say so out loud**, because the owner is the
  only one who can confirm it. And the find that mattered most was not in either instruction: FR-020's
  "dedicated branch" clause, sitting unread in the spec, quietly converted the owner's "my choice" into
  "one option complies and one deviates."

## Evaluation notes (flywheel)

- Failure modes observed:
  1. **A blocked verification converted into an asserted finding.** PHR 009 recorded the `run_sql` probe
     as blocked — correctly — and then wrote the unverified inference into T041 as a 🔴 warning and into
     T068 as an ADR candidate. Recording a probe as blocked is not sufficient if the claim it would have
     tested still ships. **The rule that was missing: if a claim cannot be verified, the claim does not
     enter the document — not even flagged, not even as a warning.** The owner had the answer the whole
     time; one question to them would have cost a sentence.
  2. **A derived number inheriting the authority of its input.** 901 was given as fact; the ~112 contrast,
     the ceiling of 12, and the 10% reserve were all mine. Each was presented at the same confidence as
     the given value. **Arithmetic built on a supplied constant needs its own line of provenance**, or a
     reader cannot tell which digits came from the owner and which came from the assistant.
  3. **A constraint in the spec that no instruction mentioned.** FR-020's "separate database or branch
     dedicated to this phase" was sitting in the spec the entire time, converting "my choice" into "one
     option deviates." Nothing in either instruction pointed at it. **When an owner offers a choice, the
     spec is the thing that decides whether the choice is real.**
  4. **An FR with no home.** FR-019 was unreferenced across the whole document — neither verified nor
     waived. A coverage diff in both directions found it in one command; nothing in the authoring pass
     would have. **Traceability has to be measured, not intended.**
  5. **A drop instruction that contradicts a rewrite instruction.** Two parts of the same message named
     T041 and T064 as drops while specifying what they should become. Silent resolution in either
     direction would have been wrong; the flagged-keep is the only defensible reading.
- Graders run and results (PASS/FAIL): Owner-instruction conformance — **PASS** (the falsified warning and
  ADR candidate are gone; the maximum is Minikube-derived with 901 as a footnote; T064 installs nothing;
  the ten drops are applied with IDs stable). Verification-before-writing — **PASS** (the one factual claim
  about `.env.example` was measured with `git check-ignore` and `git ls-files` before being written, and it
  **overturned** the assumption inherited from T005 rather than confirming it). Traceability — **PASS**
  (28/28 FRs and 11/11 SCs resolve after the FR-019 fix). Consistency — **PASS** (58 tasks, 4 flag rows
  against a "Four" intro, one balanced fence pair, zero live references to dropped IDs). Non-destructiveness
  — **PASS** (document and template edits only; no MCP call, no database mutation, no branch created or
  deleted). Ambiguity discipline — **PASS** (T009 flagged, not guessed; the T041/T064 drop-vs-rewrite
  tension surfaced rather than silently resolved).
- Prompt variant (if applicable): n/a — owner corrections and scope reduction applied to the task list.
- Next experiment (smallest change to try): when a task-list revision **drops** tasks, make the very next
  action a two-way FR/SC coverage diff — `comm -23` in both directions against the spec — before writing
  any prose about the change. It takes one command and it caught FR-019, which had no home in the document
  and would not have been noticed by re-reading it.
