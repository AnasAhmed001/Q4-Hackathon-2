# syntax=docker/dockerfile:1
#
# Phase IV (D1) — multi-stage Next.js standalone build.
#
# The build stage needs devDependencies (typescript, tailwind, eslint), which
# must not ship in the final image. That is why there is a separate `deps`
# stage and why NODE_ENV=production is set only *after* `npm ci` has run.
#
# IMPORTANT: changing frontend.nodePort / backend.nodePort in values.yaml
# requires rebuilding this image. The NEXT_PUBLIC_* values below are inlined
# into the browser bundle by `next build` and cannot be corrected at runtime.

# ---------- deps: all dependencies, including dev ----------
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ---------- builder: produce .next/standalone ----------
FROM node:22-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Browser-facing addresses (FR-005, FR-006). Read out of charts/todo-chatbot/values.yaml
# by deploy/deploy.sh so the chart and the bundle cannot drift (D3).
ARG NEXT_PUBLIC_BACKEND_URL
ARG NEXT_PUBLIC_BETTER_AUTH_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
ENV NEXT_PUBLIC_BETTER_AUTH_URL=${NEXT_PUBLIC_BETTER_AUTH_URL}

# Set only now that devDependencies are already installed above.
ENV NODE_ENV=production
RUN npm run build

# ---------- runner: minimal, non-root ----------
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
# Without HOSTNAME the standalone server binds to the container hostname and is
# unreachable from the pod network — the readiness probe would never pass.
ENV HOSTNAME="0.0.0.0"

# `standalone` deliberately does NOT copy these two; they must be placed
# alongside server.js at the standalone root.
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

# Writable scratch for the Next.js cache — required because the Deployment runs
# with readOnlyRootFilesystem: true (D7). Mounted as an emptyDir by the chart.
RUN mkdir -p /app/.next/cache && chown -R node:node /app/.next

# node:22-alpine ships a `node` user at uid/gid 1000, matching the pod's
# runAsUser/runAsGroup (FR-017).
USER node

EXPOSE 3000

CMD ["node", "server.js"]
