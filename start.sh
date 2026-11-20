#!/usr/bin/env bash
# Start SewaCircle locally on macOS/Linux: backend (offline replay mode) on :8000 and the website on :5173.
# Usage (from the repo root):  bash start.sh            (or SEWA_API_PORT=8010 bash start.sh if port 8000 is taken)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export SEWA_API_PORT="${SEWA_API_PORT:-8000}"
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  echo "Creating Python environment (first run only)..."
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/python" -m pip install -r "$ROOT/backend/requirements.txt"
fi
[ -d "$ROOT/frontend/node_modules" ] || (cd "$ROOT/frontend" && npm ci)
(cd "$ROOT/backend" && SEWA_LLM_MODE=replay "$ROOT/.venv/bin/python" -m uvicorn app.main:app --port "$SEWA_API_PORT") &
BACKEND=$!
trap 'kill $BACKEND 2>/dev/null' EXIT
echo "Backend starting on http://127.0.0.1:$SEWA_API_PORT ..."
cd "$ROOT/frontend" && npm run dev
