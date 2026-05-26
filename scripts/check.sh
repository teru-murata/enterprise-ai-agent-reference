#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"
NPM_BIN="${NPM:-npm}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run_step() {
  local name="$1"
  shift
  echo
  echo "==> ${name}"
  "$@"
}

run_step "Backend tests" bash -c "cd '${REPO_ROOT}/apps/api' && '${PYTHON_BIN}' -m pytest"
run_step "MCP policy server tests" bash -c "cd '${REPO_ROOT}/mcp/policy_server' && '${PYTHON_BIN}' -m pytest"
run_step "Frontend typecheck" bash -c "cd '${REPO_ROOT}/apps/web' && '${NPM_BIN}' run typecheck"
run_step "Frontend build" bash -c "cd '${REPO_ROOT}/apps/web' && '${NPM_BIN}' run build"
run_step "Dataset ingest and retrieval evals" bash -c "cd '${REPO_ROOT}' && '${PYTHON_BIN}' scripts/ingest_docs.py && '${PYTHON_BIN}' scripts/run_evals.py"

echo
echo "All local validation checks passed."
