output "api_alb_dns_name" {
  description = "ALB DNS name for the API. Add auth/API gateway before production exposure."
  value       = module.api_service.alb_dns_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = module.api_service.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name."
  value       = module.api_service.service_name
}

output "documents_bucket_name" {
  description = "Synthetic documents bucket name."
  value       = module.documents.bucket_name
}

output "rds_endpoint" {
  description = "RDS endpoint. Do not expose publicly."
  value       = module.database.db_instance_endpoint
}

output "openai_secret_arn" {
  description = "Secrets Manager ARN for the OpenAI API key container."
  value       = module.secrets.openai_api_key_secret_arn
}
