# AWS Deployment Skeleton

M9 adds an AWS deployment skeleton for discussion and review. It does not create AWS resources by default, and no Terraform apply has been run.

## Architecture Overview

The planned AWS deployment maps the local reference stack to managed AWS services:

- ECS Fargate runs the FastAPI backend container.
- ECR stores the API container image.
- RDS PostgreSQL stores app data and pgvector document chunks.
- S3 stores synthetic/sample document artifacts.
- Secrets Manager stores `OPENAI_API_KEY` and database connection secrets.
- CloudWatch stores container logs and future operational metrics.
- ALB provides HTTP ingress to the API service.
- GitHub Actions uses OIDC-based AWS authentication.
- Terraform composes environment-specific infrastructure.

## Deployment Assumptions

- This is a dev-oriented skeleton, not a production-ready deployment.
- The repository contains synthetic data only.
- `OPENAI_API_KEY`, database credentials, and `DATABASE_URL` are supplied through Secrets Manager or environment configuration, never source control.
- RDS is not publicly accessible by default.
- The ALB is HTTP-only in the skeleton. Production deployment needs TLS, auth, rate limits, and ingress review.
- Audit persistence is not implemented yet.

## Manual GitHub Actions Workflow

The manual workflow lives at `.github/workflows/aws-deploy.yml`.

It requires repository or environment variables:

- `AWS_ROLE_ARN`: IAM role trusted by GitHub Actions OIDC.
- `AWS_REGION`: target AWS region.
- `ECR_REPOSITORY`: existing ECR repository name for the API image.

The workflow:

1. Checks out the repository.
2. Assumes the AWS role through OIDC.
3. Builds the API Docker image.
4. Pushes the image to ECR.
5. Runs `terraform init`.
6. Runs `terraform plan`.
7. Runs `terraform apply` only if the manual `apply` input is explicitly set to `true`.

Normal CI does not use AWS credentials and does not run this workflow.

## OIDC Trust Setup Overview

Create an AWS IAM role with a trust relationship for GitHub Actions OIDC scoped to this repository and environment. Keep permissions narrow:

- ECR push/pull for the configured repository.
- Terraform-managed resource permissions needed by the reviewed plan.
- No static access keys.
- No `AdministratorAccess`.

The exact trust policy is account-specific and intentionally not committed here.

## Terraform Plan Steps

```bash
cd infra/terraform/envs/dev
terraform init
terraform validate
terraform plan -var="api_image_uri=replace-with-ecr-image-uri"
```

Copy `backend.tf.example` only after choosing a real remote state bucket and lock table. Do not commit account-specific `backend.tf`, `terraform.tfvars`, state files, or secrets.

## pgvector Setup

After RDS PostgreSQL is provisioned, enable pgvector through a controlled migration path:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The database module documents this requirement but does not run migrations.

## Cost Warning

ECS, ALB, NAT gateways, RDS, S3, CloudWatch, and ECR can incur cost. The skeleton uses small dev defaults where possible, but operators must review the Terraform plan and pricing before applying.

## Security Limitations

- No app authentication is implemented yet.
- ALB exposure requires an auth/API gateway design before production use.
- Audit events are not persisted.
- Secrets containers are scaffolded, but secret values must be created out of band.
- IAM permissions require final least-privilege review before use.
- Database migrations and backup policies are placeholders.

## Rollback and Cleanup

Rollback should use ECS service deployment history or a previously tagged ECR image. Infrastructure cleanup should be planned with Terraform state intact. RDS deletion, final snapshots, log retention, S3 object retention, and secret recovery windows must be reviewed before destroying resources.
