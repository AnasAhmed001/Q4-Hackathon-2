#!/usr/bin/env bash
#
# Phase IV — the documented deployment procedure (T030, FR-021, SC-001).
#
#   build -> load -> secret -> helm upgrade --install -> verify
#
# Idempotent end to end: running it twice installs fresh once and updates in
# place thereafter (FR-012, SC-009), because `helm upgrade --install` is one
# command for both paths — there is no "does a release exist?" branch.
#
# Run from Git Bash at the phase root:
#     bash deploy/deploy.sh
#
# Prerequisites: Docker Desktop running. Minikube and Helm are INSTALLED BY
# THIS SCRIPT if absent (FR-021/FR-022 — they are a procedure step, not an
# assumption about the reader's machine).

set -euo pipefail

# ---------------------------------------------------------------- config ----
RELEASE="${RELEASE:-todo-chatbot}"
NAMESPACE="${NAMESPACE:-todo-chatbot}"
CHART="charts/todo-chatbot"
VALUES="$CHART/values.yaml"
ENV_FILE="${ENV_FILE:-deploy/.env.deploy}"
SECRET_NAME="todo-chatbot-secrets"
TAG="${TAG:-dev}"

# T033: a deliberate, documented allocation — NOT defaults. These are the input
# to the max-replica arithmetic stated in the README (T041). Changing them
# changes that maximum; if you change them, update the README.
CPUS="${CPUS:-4}"
# Docker Desktop on this host reports 3854MB total, so 4096 is rejected by
# minikube with MK_USAGE. 3584 leaves headroom for the host. Raise it only if
# Docker Desktop's own memory allocation is raised first (Settings → Resources).
MEMORY="${MEMORY:-3584}"
DRIVER="${DRIVER:-docker}"

# ------------------------------------------------------------- utilities ----
say()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m  ✓ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m  ! %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

require() {
  command -v "$1" >/dev/null 2>&1 || die "missing-tool: '$1' is not on PATH. $2"
}

# T031/D3: read the ports OUT of the chart rather than duplicating them, so the
# bundle cannot drift from the Service definitions. A parse failure ABORTS
# rather than silently baking 'http://localhost:' into the image.
read_port() {
  local key="$1" value
  value=$(awk -v k="^${key}:" '$0 ~ k {f=1} f && /nodePort:/ {print $2; exit}' "$VALUES")
  [ -n "$value" ] || die "port-parse-failure: could not read ${key}.nodePort from $VALUES"
  case "$value" in
    ''|*[!0-9]*) die "port-parse-failure: ${key}.nodePort='$value' is not numeric" ;;
  esac
  [ "$value" -ge 30000 ] && [ "$value" -le 32767 ] \
    || die "port-range: ${key}.nodePort=$value is outside the 30000-32767 NodePort range"
  printf '%s' "$value"
}

# ------------------------------------------------------- step 1: toolchain ----
say "Step 1/7 — toolchain (FR-021: installing it is part of this procedure)"

if ! command -v minikube >/dev/null 2>&1; then
  warn "minikube absent — installing (this is expected on a clean machine)"
  if command -v winget >/dev/null 2>&1; then
    winget install --id Kubernetes.minikube --accept-source-agreements --accept-package-agreements \
      || die "minikube-install-failed: install it manually, then re-run"
  else
    die "minikube-absent: install Minikube (https://minikube.sigs.k8s.io/docs/start/), then re-run"
  fi
fi

if ! command -v helm >/dev/null 2>&1; then
  warn "helm absent — installing"
  if command -v winget >/dev/null 2>&1; then
    winget install --id Helm.Helm --accept-source-agreements --accept-package-agreements \
      || die "helm-install-failed: install it manually, then re-run"
  else
    die "helm-absent: install Helm (https://helm.sh/docs/intro/install/), then re-run"
  fi
fi

require docker "Start Docker Desktop, then re-run."
require kubectl "Install kubectl, then re-run."

docker info >/dev/null 2>&1 || die "docker-daemon-down: start Docker Desktop, then re-run."

ok "docker $(docker version --format '{{.ServerVersion}}' 2>/dev/null)"
ok "minikube $(minikube version --short 2>/dev/null || echo present)"
ok "helm $(helm version --short 2>/dev/null)"
ok "kubectl $(kubectl version --client 2>/dev/null | awk '/Client Version/{print $3; exit}')"

# ------------------------------------------------- step 2: cluster (T033) ----
say "Step 2/7 — cluster and host reachability (T033, FR-006)"

FE_NP="$(read_port frontend)"
BE_NP="$(read_port backend)"
ok "pinned ports read from values.yaml — frontend $FE_NP, backend $BE_NP"

if ! minikube status >/dev/null 2>&1; then
  minikube start --driver="$DRIVER" --cpus="$CPUS" --memory="$MEMORY" \
    --ports="${FE_NP}:${FE_NP},${BE_NP}:${BE_NP}"
else
  ok "minikube already running"
fi

# T033 records which branch was taken. --ports is the primary mechanism; the
# port-forward fallback publishes the SAME port numbers so the image stays valid.
#
# ⚠️ curl's EXIT STATUS is not usable as the reachability test on this host.
# Under Git Bash with `-o /dev/null`, curl returns **23 (CURLE_WRITE_ERROR) even
# on a perfectly good HTTP 200** — measured directly: `http=200 curl_rc=23`.
# `if curl ...; then` therefore takes the ELSE branch for a healthy app, and the
# script warns "not reachable" while the frontend is serving fine. That is a
# false alarm that sends a reader off to the port-forward fallback for no
# reason, and it was observed firing on two runs that were both up.
#
# Test the HTTP CODE instead. It is written to stdout regardless of that write
# error, and "did it answer 200" is what reachable actually means. The `|| true`
# keeps the non-zero status from poisoning the pipeline under `set -e`.
fe_code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 "http://localhost:${FE_NP}/login" 2>/dev/null || true)
if [ "$fe_code" = "200" ]; then
  ok "host reachability via --ports: http://localhost:${FE_NP} (HTTP $fe_code)"
else
  warn "http://localhost:${FE_NP} answered HTTP ${fe_code:-none} — no release yet, or not reachable."
  warn "If it is still not answering 200 after step 6, use the documented fallback:"
  warn "  kubectl -n $NAMESPACE port-forward --address 127.0.0.1 svc/$RELEASE-frontend ${FE_NP}:3000"
  warn "  kubectl -n $NAMESPACE port-forward --address 127.0.0.1 svc/$RELEASE-backend  ${BE_NP}:7860"
fi

# ----------------------------------------------------------- step 3: build ---
say "Step 3/7 — build both images (FR-001, D1)"

docker build -f backend-api/Dockerfile -t "todo-chatbot-backend:${TAG}" backend-api/
ok "built todo-chatbot-backend:${TAG}"

# NEXT_PUBLIC_* are compile-time constants inlined by `next build` (D3).
docker build -f frontend/Dockerfile \
  --build-arg "NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:${FE_NP}" \
  --build-arg "NEXT_PUBLIC_BACKEND_URL=http://localhost:${BE_NP}" \
  -t "todo-chatbot-frontend:${TAG}" frontend/
ok "built todo-chatbot-frontend:${TAG}"

# ----------------------------- step 4: post-build proof (T034, D3 layer 3) ---
say "Step 4/7 — prove the declared ports actually landed in the bundle (T034)"

for URL in "localhost:${FE_NP}" "localhost:${BE_NP}"; do
  docker run --rm --entrypoint sh "todo-chatbot-frontend:${TAG}" \
    -c "grep -rq '${URL}' .next/static && echo BAKED_OK" \
    | grep -q BAKED_OK || die "stale-bundle: '${URL}' not found in .next/static — rebuild required"
  ok "BAKED_OK: ${URL}"
done

# Without this value baked, api-client.ts falls back to :8000 while the backend
# listens on 7860 — a dead-port failure that looks like an application bug.
#
# T064 step 4: no .env at EITHER location. Checked inside the image, so this is
# the check that actually tests T013's .dockerignore.
#
# NOTE: `grep -c` exits 1 when it matches nothing. Under `set -o pipefail` that
# status becomes the pipeline's, which would fail this gate on a CLEAN image.
# The `|| true` neutralises it at the source, so the COUNT decides, not grep's
# exit code.
for dir in / /app; do
  envcount=$(docker run --rm --entrypoint sh "todo-chatbot-frontend:${TAG}" \
    -c "ls -a ${dir} | grep -c '^\.env' || true")
  [ "$envcount" = "0" ] \
    || die "secret-in-image: ${envcount} .env file(s) in ${dir} of the frontend image (check frontend/.dockerignore)"
done
ok "no .env baked into the frontend image (/ and /app both clean)"

# ------------------------------------------------------------ step 5: load ---
say "Step 5/7 — make the images available to the cluster (spec edge case)"

# ⚠️ `minikube image load` SILENTLY NO-OPS when the node already holds an image
# under the same tag. It prints nothing, exits 0, and leaves the OLD image in
# place — so the script would report success while shipping the previous build.
#
# The tag here is the constant `dev`, so this bites on every RE-RUN over an
# existing cluster. It does NOT bite on a clean cluster, where no tag exists to
# collide with — which is exactly why the fresh-install path looked perfect and
# the update path (FR-012, SC-009) was broken. Observed directly: the node's
# `dev` still resolved to the 8-day-old image after `deploy.sh` reported
# "✓ loaded both images", and the pod kept running old code while carrying new
# ConfigMap values.
#
# Drop the stale tag first so the load is a real import. `-f` is required
# because a running pod may still reference it; the container keeps running —
# it is only untagged — and step 7 restarts the pods anyway.
for img in "todo-chatbot-backend:${TAG}" "todo-chatbot-frontend:${TAG}"; do
  minikube ssh -- sudo docker rmi -f "$img" >/dev/null 2>&1 || true
done

minikube image load "todo-chatbot-backend:${TAG}"
minikube image load "todo-chatbot-frontend:${TAG}"
ok "loaded both images into minikube"

# ---------------------------------------------------------- step 6: secret ---
say "Step 6/7 — materialize the Secret (T027, FR-007, FR-010)"

[ -f "$ENV_FILE" ] || die "no-env-file: $ENV_FILE not found. Copy deploy/.env.deploy.example and fill it in."

# The namespace must exist before the Secret can live in it. Step 7's
# --create-namespace runs too late for this, so create it here instead — and
# declaratively, so this is an apply like everything else rather than a
# mutation (FR-003). Idempotent: a second run reports `unchanged`.
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml 2>/dev/null \
  | kubectl apply -f - >/dev/null
ok "namespace $NAMESPACE present"

# Declarative-shaped and idempotent: running this twice reports `unchanged` the
# second time — an update, not a duplicate (constitution I).
# No credential is ever echoed.
#
# ⚠️ `kubectl create secret --from-env-file` does NOT strip surrounding quotes
# from a value, the way docker-compose does. A quoted `DATABASE_URL="postgres://…"`
# therefore ships the quote characters INTO the Secret, and the backend dies at
# import with:
#     Could not parse SQLAlchemy URL from string '"postgresql://…"'
# Quoting is legitimate .env style, so normalize rather than forbid it.
#
# ⚠️ The normalized file must be a RELATIVE path. kubectl here is a native
# Windows binary while this script runs under Git Bash: `mktemp` returns
# `/tmp/tmp.XXXX`, which kubectl cannot resolve ("The system cannot find the
# path specified") — and with `MSYS_NO_PATHCONV=1` Git Bash will not translate
# it. A relative path is resolved from the working directory and works.
# It is 0600, removed on exit, and covered by .gitignore.
tmpenv="deploy/.env.deploy.normalized.$$"
trap 'rm -f "$tmpenv"' EXIT
( umask 077; : > "$tmpenv" )
while IFS= read -r line; do
  case "$line" in
    ''|'#'*) printf '%s\n' "$line"; continue ;;
  esac
  key="${line%%=*}"; val="${line#*=}"
  case "$val" in
    \"*\") val="${val#\"}"; val="${val%\"}" ;;
    \'*\') val="${val#\'}"; val="${val%\'}" ;;
  esac
  printf '%s=%s\n' "$key" "$val"
done < "$ENV_FILE" > "$tmpenv"

# stderr is deliberately NOT suppressed here. A `2>/dev/null` on this command
# is what turned a clear "cannot find the path" into the far less useful
# "error: no objects passed to apply" downstream.
secret_yaml=$(kubectl -n "$NAMESPACE" create secret generic "$SECRET_NAME" \
  --from-env-file="$tmpenv" --dry-run=client -o yaml) \
  || die "secret-create-failed: kubectl could not build the Secret from $tmpenv"
printf '%s' "$secret_yaml" | kubectl apply -f - >/dev/null \
  || die "secret-apply-failed: could not apply $SECRET_NAME in $NAMESPACE"
ok "Secret $SECRET_NAME applied in namespace $NAMESPACE"

# Every key referenced with optional:false must be present, or the pods will
# refuse to start (FR-010). Fail here, with the key named, rather than at the
# kubelet with a less obvious message.
for key in DATABASE_URL BETTER_AUTH_SECRET COHERE_API_KEY; do
  kubectl -n "$NAMESPACE" get secret "$SECRET_NAME" -o "jsonpath={.data.${key}}" 2>/dev/null | grep -q . \
    || die "missing-secret-key: '$key' is not in $SECRET_NAME (referenced with optional:false)"
done
ok "all required secret keys present"

# The check that would have caught the quoting bug above: a value that still
# begins with a quote character will not parse in the application.
for key in DATABASE_URL BETTER_AUTH_SECRET COHERE_API_KEY; do
  first=$(kubectl -n "$NAMESPACE" get secret "$SECRET_NAME" -o "jsonpath={.data.${key}}" 2>/dev/null \
    | base64 -d 2>/dev/null | cut -c1 || true)
  case "$first" in
    '"'|"'") die "quoted-secret-value: '$key' begins with a quote character — the app will not parse it" ;;
  esac
done
ok "no secret value is quote-wrapped"

# ----------------------------------------------------------- step 7: install -
say "Step 7/7 — install or update the release, then verify (FR-002, FR-012)"

# ONE command for both fresh install and in-place update — that is what makes
# FR-012/SC-009 hold with no existence check. --wait blocks on readiness.
helm upgrade --install "$RELEASE" "$CHART" \
  -n "$NAMESPACE" --create-namespace --wait --timeout 5m

# ⚠️ helm does NOT roll the pods here, and the release still reports `deployed`.
# Nothing in the pod template differs between two builds — the image tag is the
# constant `dev` — so there is no template diff to trigger a rollout, and helm
# never restarts pods merely because a ConfigMap they mount has changed.
#
# Left alone, the upgrade is a no-op on the running workload: the release moves
# to a new revision while the pods keep the PREVIOUS image AND the previous
# environment. That is how a corrected `BACKEND_URL` reached the ConfigMap but
# not the frontend pod. Restart explicitly so what is running matches what was
# declared. (On a fresh install this is a redundant but harmless second rollout.)
kubectl -n "$NAMESPACE" rollout restart deploy
kubectl -n "$NAMESPACE" rollout status deploy --timeout=5m

kubectl -n "$NAMESPACE" get pods -o wide

printf '\n\033[1;32mDeployment complete.\033[0m\n'
printf '  Frontend : http://localhost:%s\n' "$FE_NP"
printf '  Backend  : http://localhost:%s/health\n\n' "$BE_NP"
printf '  If those are not reachable, start the port-forward fallback:\n'
printf '    kubectl -n %s port-forward --address 127.0.0.1 svc/%s-frontend %s:3000\n' "$NAMESPACE" "$RELEASE" "$FE_NP"
printf '    kubectl -n %s port-forward --address 127.0.0.1 svc/%s-backend  %s:7860\n\n' "$NAMESPACE" "$RELEASE" "$BE_NP"
