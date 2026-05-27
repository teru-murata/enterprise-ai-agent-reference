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

if ([string]::IsNullOrWhiteSpace($Profile)) {
    throw "Profile is required."
}
if ([string]::IsNullOrWhiteSpace($Region)) {
    throw "Region is required."
}
if ([string]::IsNullOrWhiteSpace($ExpectedAccountId)) {
    throw "ExpectedAccountId is required."
}

Write-Host "AWS CLI preflight"
Write-Host "Profile: $Profile"
Write-Host "Region: $Region"
Write-Host "Expected account id: $ExpectedAccountId"

Write-Host "`nAWS CLI version:"
& $AwsCliPath --version
if ($LASTEXITCODE -ne 0) {
    throw "AWS CLI version check failed."
}

Write-Host "`nAWS CLI configure list:"
& $AwsCliPath configure list --profile $Profile
if ($LASTEXITCODE -ne 0) {
    Write-Warning "aws configure list failed for the selected profile. Continuing to caller identity check."
}

$account = & $AwsCliPath sts get-caller-identity `
    --profile $Profile `
    --region $Region `
    --query Account `
    --output text
if ($LASTEXITCODE -ne 0) {
    throw "aws sts get-caller-identity failed."
}

$callerArn = & $AwsCliPath sts get-caller-identity `
    --profile $Profile `
    --region $Region `
    --query Arn `
    --output text
if ($LASTEXITCODE -ne 0) {
    throw "aws sts get-caller-identity ARN lookup failed."
}

$account = "$account".Trim()
$callerArn = "$callerArn".Trim()

if ($account -ne $ExpectedAccountId) {
    throw "AWS account mismatch. Expected $ExpectedAccountId but caller identity returned $account."
}

Write-Host "`nPreflight passed."
Write-Host "Safe AWS caller metadata:"
Write-Host "- profile: $Profile"
Write-Host "- region: $Region"
Write-Host "- account_id: $account"
Write-Host "- caller_arn: $callerArn"
