# T064 — Credential Scan Evidence

**Task**: 🔒 Credential scan over tracked files, git history, and both built images — with no new tool installs.
**Satisfies**: SC-004.
**Date**: 2026-10-01
**Tools**: `git`, `grep`, `tar`, `docker` only. **No scanner was installed** — TruffleHog is not selected and must not be installed; gitleaks and `docker scout` are equally out (§T064).

**Scope** (per the spec's clarification): "the repository" means **git-tracked files and git history**. Untracked working-tree files — `.env`, `.env.local`, `frontend/.env`, `backend-api/.env`, all verified gitignored — are explicitly **out of scope** as *search targets*, but were used as the **needle source** so the scan searches for the project's real values, not just generic shapes. **Both built images are in scope.**

---

## 1. Result summary

| Surface | Status |
|---|---|
| Tracked files — generic patterns | ✅ CLEAN — all 46 hits are documentation placeholders |
| Tracked files — real values | ✅ CLEAN — 0 hits for every live credential |
| Git history — generic patterns | 🔴 **LEAK FOUND** — see §3 |
| Git history — real values | 🔴 **LEAK FOUND** — see §3 |
| Built images | ⏳ **PENDING** — blocked on the Docker daemon (§5) |

---

## 2. Tracked files — CLEAN

Pattern: `AIza[0-9A-Za-z_-]{35}|npg_[A-Za-z0-9]{8,}|postgres(ql)?://[^:]+:[^@]+@|sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----`

- `git grep -nIE` → **46 hits**, and `git ls-files -z | xargs -0 grep -lIE` → **36 files**. Every hit is a skill-template placeholder: `postgresql://user:password@localhost:5432/dbname`, `ep-xxx.neon.tech`, `[user]:password@[endpoint]`. **No real credential.**
- `AIza…` (Google API key shape): **0 hits**. `-----BEGIN … PRIVATE KEY-----`: **0 hits**.
- Real values from the live env files, searched with `git grep -F` and `git log --all -S`: **0 hits for every one** — `COHERE_API_KEY` (40 chars), `DATABASE_URL_UNPOOLED` (141), and one `DATABASE_URL` variant (148).

> Note on a self-inflicted artifact: an early redaction pass rewrote `001-task-management-api` as `001-task-<REDACTED>` because my mask rule matched the `sk-` inside "ta**sk-m**anagement". That is a masking artifact, **not** a finding.

---

## 3. 🔴 Git history — LEAK CONFIRMED

A **real, currently-live credential set** is committed in git history. It is **absent from every branch tip** — the file was deleted — but it is fully recoverable from the objects.

**File**: `phase-2-fullstack-todo-app/backend-api/.env.example`
**Added**: `5fa9872` · **Modified**: `6b62efb` · **Deleted**: `baf3496` ("chore: remove example environment configuration file")

| Leaked value | Evidence | Still live? |
|---|---|---|
| Neon password `npg_…` | 6 occurrences of the `npg_[A-Za-z0-9]{8,}` shape in `git log -p --all`; matched by `-S` in **3** commits | 🔴 **YES** — byte-identical to the password in the current `.env` files |
| `DATABASE_URL` (124-char form) | `git log --all -S` → 3 introducing commits | 🔴 **YES** — matches the live value |
| `DATABASE_URL` (148-char form, `channel_binding`) | present in the same historical file | ⚠️ superseded variant of the same endpoint |
| `BETTER_AUTH_SECRET` (44 chars) | `git log --all -S` → 2 introducing commits | 🔴 **YES** — byte-identical to the live `.env` |
| `NEON_DATABASE_URL` | same historical file, same endpoint & password | 🔴 **YES** |

Host in the leaked URL: `ep-falling-sea-ahjyhl6i-pooler.c-3.us-east-1.aws.neon.tech`, role `neondb_owner`.

**This is the same database and the same secret that Phase IV deploys with.** FR-020 targets the existing Neon database on `main`, so the credential in history is the credential in production for this deployment.

### Why the tracked-file scan passed anyway

`git grep` searches the **working tree of tracked files**. The file no longer exists, so nothing surfaced. Only the history scan (`git log -p --all` + `git log --all -S`) finds it. A "clean" `git grep` is **not** evidence of a clean repository — this is exactly the false-negative the scan is designed to catch.

### Status

**SC-004 is NOT SATISFIED.** Reported to the owner. Remediation is a **human decision** — both paths are consequential, and neither was taken autonomously:

1. **Rotate** the Neon password and `BETTER_AUTH_SECRET`, then update `.env.deploy`. Cheap, does not rewrite shared history, and is **required regardless** — the value is compromised the moment it is in a pushed commit. Rotation alone leaves the old value readable in history, but the old value stops working.
2. **Rewrite history** (`git filter-repo` / BFG) to purge the blob. Breaks every existing clone and any open PR; must be coordinated with anyone who has pulled `phase-2-fullstack-todo-app`.

**Recommendation: do (1) now; treat (2) as optional and coordinate it.** Rotation is the security fix; history rewriting is hygiene.

---

## 4. Command set used (reproducible, no installs)

```bash
P='AIza[0-9A-Za-z_-]{35}|npg_[A-Za-z0-9]{8,}|postgres(ql)?://[^:]+:[^@]+@|sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'

git grep -nIE "$P"                                  # tracked files
git ls-files -z | xargs -0 grep -lIE "$P"           # anything git grep skips
git log -p --all | grep -nIE "$P"                   # full history, deleted lines included
git log --all -S'<literal value>' --oneline         # per-value: the commit that introduced it
```

`grep -F` for literal values (they contain regex metacharacters); `-E` for the generic patterns.

---

## 5. ⏳ Images — PENDING

Cannot run: the Docker daemon is **down** (`npipe:////./pipe/dockerDesktopLinuxEngine` not found) and the images are not built yet.

```bash
for img in todo-chatbot-backend:dev todo-chatbot-frontend:dev; do
  rm -rf /tmp/scan && mkdir -p /tmp/scan
  docker save "$img" -o /tmp/scan/img.tar
  tar -xf /tmp/scan/img.tar -C /tmp/scan
  grep -rlIE "$P" /tmp/scan && echo "HIT in $img" || echo "clean: $img"
done
```

**🔴 Layer-format check before trusting a clean result.** `grep` finds plaintext inside uncompressed `layer.tar` entries. If Docker emits **gzipped** layers (OCI layout), a plain `grep` reports *clean* on a compressed blob — a **false negative**. Decompress first if so:

```bash
find /tmp/scan -name '*.tar.gz' -exec sh -c \
  'tar -xzOf "$1" | grep -aIE "'"$P"'" && echo "HIT $1"' _ {} \;
```

**Which form actually applied must be recorded in this file when the scan runs.**

`frontend/.dockerignore` (T013) already excludes `.env`, `.env.*` and `*.pem` from the frontend build context, and `backend-api/.dockerignore` excludes `.env`/`.env.*` — so a clean result is expected. It still has to be **proved**, not assumed.
