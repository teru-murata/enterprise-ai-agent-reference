param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $env:OPENAI_API_KEY) {
    Write-Error "OPENAI_API_KEY is required for OpenAI embedding validation."
}

$env:EMBEDDING_PROVIDER = "openai"
$env:OPENAI_EMBEDDING_MODEL = if ($env:OPENAI_EMBEDDING_MODEL) {
    $env:OPENAI_EMBEDDING_MODEL
}
else {
    "text-embedding-3-small"
}
$env:OPENAI_EMBEDDING_DIMENSIONS = if ($env:OPENAI_EMBEDDING_DIMENSIONS) {
    $env:OPENAI_EMBEDDING_DIMENSIONS
}
else {
    "16"
}

Push-Location $RepoRoot
try {
    @'
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
'@ | & $Python
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}
