#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is required for OpenAI embedding validation." >&2
  exit 1
fi

export EMBEDDING_PROVIDER="openai"
export OPENAI_EMBEDDING_MODEL="${OPENAI_EMBEDDING_MODEL:-text-embedding-3-small}"
export OPENAI_EMBEDDING_DIMENSIONS="${OPENAI_EMBEDDING_DIMENSIONS:-16}"

cd "${REPO_ROOT}"
"${PYTHON_BIN}" - <<'PY'
import os
import sys
from pathlib import Path

repo_root = Path.cwd()
sys.path.insert(0, str(repo_root / "apps" / "api"))

from app.rag.embeddings import embed_text

embedding = embed_text("synthetic incident support policy", provider="openai")
print("provider: openai")
print(f"model: {os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')}")
print(f"embedding length: {len(embedding)}")
PY
