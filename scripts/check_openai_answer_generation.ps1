param(
    [string]$Python = "python",
    [switch]$VerboseAnswer
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $env:OPENAI_API_KEY) {
    Write-Error "OPENAI_API_KEY is required for OpenAI answer generation validation."
}

$env:ANSWER_PROVIDER = "openai"
$env:OPENAI_TEXT_MODEL = if ($env:OPENAI_TEXT_MODEL) { $env:OPENAI_TEXT_MODEL } else { "gpt-5.2" }
$env:OPENAI_REASONING_EFFORT = if ($env:OPENAI_REASONING_EFFORT) {
    $env:OPENAI_REASONING_EFFORT
}
else {
    "low"
}
$env:OPENAI_ANSWER_VERBOSE = if ($VerboseAnswer) { "1" } else { "0" }

Push-Location $RepoRoot
try {
    @'
import os
import sys
from pathlib import Path

repo_root = Path.cwd()
sys.path.insert(0, str(repo_root / "apps" / "api"))

from app.answers.providers import compose_answer

retrieved_chunks = [
    {
        "chunk_id": "incident_response_policy:2",
        "document_id": "incident_response_policy",
        "source_path": "datasets/sample_docs/incident_response_policy.md",
        "title": "Incident Response Policy",
        "text": "Severity 2 incidents require support leadership notification and incident commander review.",
        "score": 4,
    }
]
draft = compose_answer(
    "How should a Severity 2 incident be handled?",
    retrieved_chunks,
    provider="openai",
)
print("provider: openai")
print(f"model: {os.getenv('OPENAI_TEXT_MODEL', 'gpt-5.2')}")
print(f"answer length: {len(str(draft['answer']))}")
print(f"citation count: {len(draft['citations'])}")
print(f"requires_human_review: {draft['requires_human_review']}")
if os.getenv("OPENAI_ANSWER_VERBOSE") == "1":
    print(f"answer: {draft['answer']}")
'@ | & $Python
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}
