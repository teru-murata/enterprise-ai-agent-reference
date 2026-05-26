param(
    [string]$Python = "python",
    [string]$Npm = "npm"
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "==> $Name"
    & $Command
}

Invoke-Step "Backend tests" {
    Push-Location (Join-Path $RepoRoot "apps/api")
    try {
        & $Python -m pytest
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "MCP policy server tests" {
    Push-Location (Join-Path $RepoRoot "mcp/policy_server")
    try {
        & $Python -m pytest
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "Frontend typecheck" {
    Push-Location (Join-Path $RepoRoot "apps/web")
    try {
        & $Npm run typecheck
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "Frontend build" {
    Push-Location (Join-Path $RepoRoot "apps/web")
    try {
        & $Npm run build
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "Dataset ingest and retrieval evals" {
    Push-Location $RepoRoot
    try {
        & $Python scripts/ingest_docs.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $Python scripts/run_evals.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "All local validation checks passed."
