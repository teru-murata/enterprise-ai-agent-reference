param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required for pgvector validation but was not found on PATH."
}

$PreviousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
docker info *> $null
$DockerInfoExitCode = $LASTEXITCODE
$ErrorActionPreference = $PreviousErrorActionPreference
if ($DockerInfoExitCode -ne 0) {
    Write-Error "Docker CLI is installed, but the Docker daemon is unavailable. Start Docker Desktop and retry pgvector validation."
}

Push-Location $RepoRoot
try {
    docker compose version | Out-Host
    docker compose up -d postgres

    $env:DATABASE_URL = if ($env:DATABASE_URL) {
        $env:DATABASE_URL
    }
    else {
        "postgresql://app:app@localhost:5432/enterprise_ai_agent"
    }

    @'
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
'@ | & $Python
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}

Write-Host "pgvector validation passed."
