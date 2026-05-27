param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:RUN_MCP_STDIO_TESTS = "1"

try {
    Push-Location (Join-Path $RepoRoot "apps/api")
    try {
        & $Python -m pytest tests/test_mcp_bridge.py -k mcp_stdio
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}
finally {
    Remove-Item Env:\RUN_MCP_STDIO_TESTS -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "MCP stdio validation passed."

