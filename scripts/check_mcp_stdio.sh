#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${REPO_ROOT}/apps/api"
RUN_MCP_STDIO_TESTS=1 "${PYTHON_BIN}" -m pytest tests/test_mcp_bridge.py -k mcp_stdio

echo
echo "MCP stdio validation passed."

