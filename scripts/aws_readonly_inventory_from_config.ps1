param(
    [string]$ConfigPath = ".local/aws-dev.json"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "AWS config file not found: $ConfigPath. Copy .local/aws-dev.example.json to .local/aws-dev.json and fill local values."
}

$config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

& (Join-Path $scriptDir "aws_readonly_inventory.ps1") `
    -AwsCliPath $config.awsCliPath `
    -Profile $config.profile `
    -Region $config.region `
    -ExpectedAccountId $config.expectedAccountId
