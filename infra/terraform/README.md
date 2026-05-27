# Terraform AWS Deployment Skeleton

This Terraform tree is a planning scaffold for the enterprise AI agent reference stack. It is intentionally small, environment-oriented, and safe to review before any real deployment work.

No AWS resources are created by this repository unless an operator explicitly configures AWS credentials, runs Terraform, reviews a plan, and applies it. Do not commit Terraform state, `.env` files, real account IDs, real ARNs, database passwords, OpenAI API keys, or customer data.

## Layout

- `envs/dev`: example development environment composition.
- `modules/network`: VPC, public/private subnet, and basic routing scaffold.
- `modules/ecs_service`: ECS Fargate, ALB, task definition, and CloudWatch log group scaffold.
- `modules/rds_pgvector`: private PostgreSQL RDS scaffold for pgvector-backed retrieval.
- `modules/s3_documents`: synthetic document bucket scaffold with public access blocked.
- `modules/secrets`: Secrets Manager secret container scaffold without secret values.
- `modules/observability`: CloudWatch log and dashboard placeholders.

## Local Review Commands

```bash
terraform fmt -recursive infra/terraform
cd infra/terraform/envs/dev
terraform init
terraform validate
terraform plan -var="api_image_uri=replace-me"
```

Do not run `terraform apply` unless explicitly requested and after reviewing cost, IAM, network exposure, and cleanup implications.
