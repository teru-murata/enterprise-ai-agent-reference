# AWS CLI Operations Safety

This repository includes AWS CLI preflight and read-only inventory scripts for future Codex-assisted AWS operations. These scripts are safety gates only. They do not create, update, or delete AWS resources.

M9 also adds an AWS deployment skeleton under `infra/terraform` and a manual GitHub Actions workflow. Terraform apply remains forbidden unless explicitly requested in the current task.

## Purpose

The preflight step verifies that an operator is using the intended AWS profile, region, and account before any AWS CLI discovery or deployment planning. It must pass before Codex runs AWS commands in a session that has AWS CLI access.

## Recommended Profile

Use a dedicated AWS CLI profile for this repository, for example:

```text
enterprise-ai-agent-dev
```

The role behind that profile should be scoped to the minimum permissions needed for the current task. Prefer read-only permissions during preflight and inventory.

## Required Inputs

- `Profile`: explicit AWS CLI profile name.
- `Region`: explicit AWS region.
- `ExpectedAccountId`: the exact 12-digit AWS account ID expected for the session.

Preflight fails if any required input is missing or if STS reports a different account ID.

## Run Preflight

PowerShell:

```powershell
.\scripts\aws_preflight.ps1 `
  -AwsCliPath "C:\Program Files\Amazon\AWSCLIV2\aws.exe" `
  -Profile enterprise-ai-agent-dev `
  -Region ap-northeast-1 `
  -ExpectedAccountId 123456789012
```

Bash:

```bash
./scripts/aws_preflight.sh \
  --profile enterprise-ai-agent-dev \
  --region ap-northeast-1 \
  --expected-account-id 123456789012
```

## Run Read-only Inventory

PowerShell:

```powershell
.\scripts\aws_readonly_inventory.ps1 `
  -AwsCliPath "C:\Program Files\Amazon\AWSCLIV2\aws.exe" `
  -Profile enterprise-ai-agent-dev `
  -Region ap-northeast-1 `
  -ExpectedAccountId 123456789012
```

Bash:

```bash
./scripts/aws_readonly_inventory.sh \
  --profile enterprise-ai-agent-dev \
  --region ap-northeast-1 \
  --expected-account-id 123456789012
```

Inventory runs preflight first, then attempts read-only discovery for ECR repositories, ECS clusters, RDS instances, S3 buckets, Secrets Manager metadata, and CloudWatch log groups. Permission-denied results are reported clearly and do not bypass preflight failure.

## Allowed Commands During Preflight Phase

- `aws --version`
- `aws configure list`
- `aws sts get-caller-identity`
- `aws ecr describe-repositories`
- `aws ecs list-clusters`
- `aws rds describe-db-instances`
- `aws s3api list-buckets`
- `aws secretsmanager list-secrets`
- `aws logs describe-log-groups`

## Forbidden Unless Explicitly Approved

- `terraform apply`
- `terraform destroy`
- `aws delete-*`
- `aws iam attach-*`
- `aws iam put-*`
- `aws s3 rm`
- `aws s3 rb`
- `aws rds delete-*`
- `aws ecs delete-*`
- `aws secretsmanager get-secret-value`

Do not call `get-secret-value` during preflight or inventory. Secret metadata can be listed, but secret values must not be printed or stored.

## Safety Notes

- AWS operations can incur cost even when the repository contains only scaffolding.
- Use an account allowlist mindset: preflight must match the expected account ID.
- Do not commit static credentials, `.env` files, Terraform state, `terraform.tfvars`, database dumps, or secret material.
- GitHub Actions should use OIDC, not long-lived AWS access keys.
- Read-only inventory does not prove production readiness; it only verifies safe visibility into the selected account.
