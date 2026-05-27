variable "app_name" {
  description = "Application name used in resource names."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "aws_region" {
  description = "AWS region for log configuration."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for ALB and ECS security groups."
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the ECS service and ALB."
  type        = list(string)
}

variable "image_uri" {
  description = "Container image URI in ECR. Use a real value only during deployment."
  type        = string
}

variable "container_port" {
  description = "Container port exposed by the FastAPI service."
  type        = number
  default     = 8000
}

variable "desired_count" {
  description = "Desired ECS task count."
  type        = number
  default     = 1
}

variable "cpu" {
  description = "Fargate task CPU units."
  type        = number
  default     = 512
}

variable "memory" {
  description = "Fargate task memory MiB."
  type        = number
  default     = 1024
}

variable "embedding_provider" {
  description = "Default embedding provider for deployed API."
  type        = string
  default     = "deterministic"
}

variable "answer_provider" {
  description = "Default answer provider for deployed API."
  type        = string
  default     = "deterministic"
}

variable "database_url_secret_arn" {
  description = "Secrets Manager ARN containing DATABASE_URL."
  type        = string
}

variable "openai_api_key_secret_arn" {
  description = "Secrets Manager ARN containing OPENAI_API_KEY."
  type        = string
}

variable "documents_bucket_arn" {
  description = "S3 bucket ARN for synthetic/sample documents."
  type        = string
}

variable "assign_public_ip" {
  description = "Whether Fargate tasks receive public IPs. Prefer false with private subnets in production."
  type        = bool
  default     = true
}
