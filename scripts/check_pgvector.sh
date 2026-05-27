#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for pgvector validation but was not found on PATH." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker CLI is installed, but the Docker daemon is unavailable. Start Docker and retry pgvector validation." >&2
  exit 1
fi

cd "${REPO_ROOT}"
docker compose version
docker compose up -d postgres

export DATABASE_URL="${DATABASE_URL:-postgresql://app:app@localhost:5432/enterprise_ai_agent}"

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
            counts = ingest_documents_to_pgvector(connection)
            results = search_pgvector(connection, "incident escalation approval", limit=3)
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
