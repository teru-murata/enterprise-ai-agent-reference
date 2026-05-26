# Terraform scaffold for the future dev environment.
#
# This file intentionally does not create real AWS resources yet.
# Planned resources:
# - ECS Fargate cluster and services for the API and future workers
# - Application Load Balancer with HTTPS listener
# - RDS PostgreSQL with pgvector extension support
# - S3 buckets for synthetic document ingestion artifacts and eval reports
# - Secrets Manager entries for database and model provider credentials
# - CloudWatch log groups, metrics, and alarms
#
# Do not add account IDs, real ARNs, hardcoded secrets, or broad IAM policies.
#
# Example future structure:
#
# module "network" {
#   source = "../../modules/network"
#   environment = var.environment
# }
#
# module "api_service" {
#   source = "../../modules/ecs_service"
#   environment = var.environment
# }

