#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

command -v "$PYTHON_BIN" >/dev/null 2>&1 || { echo "Python 3.11+ is required."; exit 1; }
"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ is required.")
PY

"$PYTHON_BIN" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[all]"

if [ ! -f .env ] && [ -f .env.example ]; then cp .env.example .env; fi

python -m pytest -q
printf '\nAdaptiveRAG-X is installed.\nStart API: %s\nResearch: %s\n' \
  "source $VENV_DIR/bin/activate && adaptive-rag-api" \
  "source $VENV_DIR/bin/activate && adaptive-rag research \"your question\""
