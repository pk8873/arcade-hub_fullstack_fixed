#!/usr/bin/env bash
# One-click local launcher for Arcade Hub (backend + frontend).
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "==> Setting up backend (Python venv + deps)..."
cd "$ROOT/arcade-backend"
if [ ! -d "venv" ]; then python3 -m venv venv; fi
# shellcheck disable=SC1091
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env

echo "==> Starting backend on http://localhost:8000 ..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACK_PID=$!

cd "$ROOT/arcade-frontend"
echo "==> Setting up frontend (npm install)..."
[ -d node_modules ] || npm install --silent
[ -f .env ] || echo "VITE_API_URL=http://localhost:8000" > .env

echo ""
echo "================================================="
echo " Arcade Hub is starting!"
echo "   Backend  : http://localhost:8000   (docs: /docs)"
echo "   Frontend : http://localhost:5173"
echo "   Admin    : admin@gmail.com / admin123"
echo "================================================="
echo ""

trap "echo 'Stopping...'; kill $BACK_PID 2>/dev/null; exit" INT TERM
npm run dev -- --host 0.0.0.0 --port 5173
kill $BACK_PID 2>/dev/null || true
