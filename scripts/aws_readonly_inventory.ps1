param(
    [string]$AwsCliPath = "aws",
    [Parameter(Mandatory = $true)]
    [string]$Profile,
    [Parameter(Mandatory = $true)]
    [string]$Region,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedAccountId
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

& (Join-Path $scriptDir "aws_preflight.ps1") `
    -AwsCliPath $AwsCliPath `
    -Profile $Profile `
    -Region $Region `
    -ExpectedAccountId $ExpectedAccountId

function Invoke-ReadOnlyInventory {
    param(
        [string]$Title,
        [string[]]$Arguments
    )

    Write-Host "`n==> $Title"
    & $AwsCliPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "$Title failed. This may be expected if the selected role lacks read-only permission."
    }
}

Write-Host "`nRead-only AWS inventory"
Write-Host "No create, update, delete, or secret-value commands are executed."

Invoke-ReadOnlyInventory "ECR repositories" @(
    "ecr", "describe-repositories",
    "--profile", $Profile,
    "--region", $Region,
    "--output", "table"
)

Invoke-ReadOnlyInventory "ECS clusters" @(
    "ecs", "list-clusters",
    "--profile", $Profile,
    "--region", $Region,
    "--output", "table"
)

Invoke-ReadOnlyInventory "RDS DB instances" @(
    "rds", "describe-db-instances",
    "--profile", $Profile,
    "--region", $Region,
    "--output", "table"
)

Invoke-ReadOnlyInventory "S3 buckets" @(
    "s3api", "list-buckets",
    "--profile", $Profile,
    "--region", $Region,
    "--output", "table"
)

Invoke-ReadOnlyInventory "Secrets Manager secret metadata" @(
    "secretsmanager", "list-secrets",
    "--profile", $Profile,
    "--region", $Region,
    "--output", "table"
)

Invoke-ReadOnlyInventory "CloudWatch log groups" @(
    "logs", "describe-log-groups",
    "--profile", $Profile,
    "--region", $Region,
    "--output", "table"
)
