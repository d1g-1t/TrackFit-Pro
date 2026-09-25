#!/usr/bin/env bash
# Per-boot service reconciliation for the TrackFit Pro API dev environment.
# Must tolerate restarts, avoid duplicate processes, and return.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export PATH="$HOME/.local/bin:$PATH"

echo "==> Ensuring .env exists"
[ -f .env ] || cp .env.example .env

echo "==> Starting PostgreSQL"
sudo pg_ctlcluster 16 main start 2>/dev/null || true
for _ in $(seq 1 30); do
  pg_isready -h localhost -p 5432 >/dev/null 2>&1 && break
  sleep 1
done

echo "==> Starting Redis"
redis-cli ping >/dev/null 2>&1 || sudo redis-server --daemonize yes --port 6379

echo "==> Applying pending database migrations"
uv run alembic upgrade head || true

echo "==> Services ready"
