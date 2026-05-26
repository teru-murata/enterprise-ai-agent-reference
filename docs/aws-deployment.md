# AWS Deployment Plan

This repository includes only an AWS deployment plan and commented Terraform scaffold. It does not create real AWS resources yet.

## Planned Services

- ECS Fargate: run the FastAPI backend, future workers, and MCP-compatible services.
- Application Load Balancer: expose the API through a managed HTTPS entry point.
- RDS PostgreSQL with pgvector: store application metadata, audit records, and vector embeddings.
- S3: store source documents, ingestion artifacts, and evaluation reports.
- AWS Secrets Manager: hold model provider credentials and database credentials.
- CloudWatch: collect logs, metrics, alarms, and operational dashboards.
- GitHub Actions: run tests, builds, static checks, and future deployment workflows.
- Terraform: define repeatable infrastructure with environment-specific variables.

## Deployment Flow

1. GitHub Actions runs backend, MCP, and frontend checks.
2. Container images are built and scanned.
3. Terraform plans infrastructure changes for review.
4. Approved changes are applied by an authorized operator.
5. ECS services deploy new images with health checks and rollback.

## Security Notes

The future deployment should use least-privilege IAM roles, private subnets for services and databases, encrypted storage, structured audit logs, and controlled access to secrets.

The current Terraform files intentionally avoid account IDs, ARNs, broad IAM permissions, and concrete resources that could be applied accidentally.

