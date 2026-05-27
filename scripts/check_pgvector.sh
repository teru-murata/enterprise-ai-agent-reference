#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${REPO_ROOT}"

if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "Using DATABASE_URL from environment."
else
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required for local pgvector validation when DATABASE_URL is not set." >&2
    exit 1
  fi

  if ! docker info >/dev/null 2>&1; then
    echo "Docker CLI is installed, but the Docker daemon is unavailable. Start Docker or set DATABASE_URL and retry pgvector validation." >&2
    exit 1
  fi

  docker compose version
  docker compose up -d postgres
  export DATABASE_URL="postgresql://app:app@localhost:5432/enterprise_ai_agent"
fi

"${PYTHON_BIN}" - <<'PY'
import time
import sys
from pathlib import Path

repo_root = Path.cwd()
sys.path.insert(0, str(repo_root / "apps" / "api"))

from app.db.connection import connect
from app.rag.pgvector_store import (
    initialize_schema,
    ingest_documents_to_pgvector,
    search_pgvector,
)

last_error = None
for _ in range(30):
    try:
        with connect() as connection:
            initialize_schema(connection)
            counts = ingest_documents_to_pgvector(connection, embedding_provider="deterministic")
            results = search_pgvector(
                connection,
                "incident escalation approval",
                limit=3,
                embedding_provider="deterministic",
            )
        if not results:
            raise SystemExit("pgvector search returned no results")
        print(f"Ingested documents: {counts['documents']}")
        print(f"Ingested chunks: {counts['chunks']}")
        print(f"Result count: {len(results)}")
        print(f"Top result: {results[0]['source_path']} score={results[0]['score']:.3f}")
        raise SystemExit(0)
    except Exception as error:
        last_error = error
        time.sleep(2)

raise SystemExit(f"pgvector validation failed: {last_error}")
PY

echo "pgvector validation passed."
