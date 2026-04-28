#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python}"
VENV_DIR="${VENV_DIR:-.venv}"
HOST="${APP_HOST:-127.0.0.1}"
PORT="${APP_PORT:-8000}"
SKIP_INSTALL="${SKIP_INSTALL:-0}"

if [ "$SKIP_INSTALL" = "1" ]; then
  RUNNER_PYTHON="$PYTHON_BIN"
else
  if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
  fi

  if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Virtual environment is missing Python at $VENV_DIR/bin/python" >&2
    exit 1
  fi

  "$VENV_DIR/bin/python" -m pip install -e ".[dev]"
  RUNNER_PYTHON="$VENV_DIR/bin/python"
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add GROQ_API_KEY and TAVILY_API_KEY before generating blogs."
fi

echo "Starting Blog Generator at http://$HOST:$PORT"
exec "$RUNNER_PYTHON" -m uvicorn blog_generator.app:create_app \
  --factory \
  --host "$HOST" \
  --port "$PORT"
