#!/usr/bin/env bash
# Idempotent bootstrap for the TrackFit Pro API dev environment.
# Runs once after checkout (and again on demand); must terminate and be re-runnable.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Installing system packages (postgres, redis, build tools)"
if ! command -v psql >/dev/null 2>&1 || ! command -v redis-server >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    postgresql postgresql-contrib redis-server build-essential libpq-dev
fi

echo "==> Installing uv"
if [ ! -x "$HOME/.local/bin/uv" ] && ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

echo "==> Installing Python dependencies (uv sync)"
uv sync --all-extras

echo "==> Creating .env from .env.example if missing"
[ -f .env ] || cp .env.example .env

echo "==> Starting PostgreSQL to provision role/database"
sudo pg_ctlcluster 16 main start 2>/dev/null || true
for _ in $(seq 1 30); do
  pg_isready -h localhost -p 5432 >/dev/null 2>&1 && break
  sleep 1
done

echo "==> Ensuring database role and database exist"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='trackfit_user'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE ROLE trackfit_user LOGIN PASSWORD 'trackfit_password';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='trackfit_pro'" | grep -q 1 \
  || sudo -u postgres createdb -O trackfit_user trackfit_pro
sudo -u postgres psql -d trackfit_pro -c "GRANT ALL ON SCHEMA public TO trackfit_user;" >/dev/null

echo "==> Applying database migrations"
uv run alembic upgrade head

echo "==> Install complete"
