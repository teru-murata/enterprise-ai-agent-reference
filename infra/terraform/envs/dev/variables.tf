variable "app_name" {
  description = "Application name."
  type        = string
  default     = "enterprise-ai-agent-reference"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region."
  type        = string
  default     = "us-east-1"
}

variable "api_image_uri" {
  description = "ECR image URI for the FastAPI API container. Replace before planning a real deploy."
  type        = string
}

variable "allowed_http_cidrs" {
  description = "CIDR ranges allowed to reach the ALB HTTP listener. Avoid 0.0.0.0/0 unless explicitly approved for dev."
  type        = list(string)
}

variable "ecs_assign_public_ip" {
  description = "Whether Fargate tasks receive public IPs. True is dev convenience; false is preferred for private subnet deployments."
  type        = bool
  default     = true
}

variable "ecr_repository_name" {
  description = "ECR repository name for the API image."
  type        = string
  default     = "enterprise-ai-agent-reference-api"
}

variable "documents_bucket_name" {
  description = "Globally unique S3 bucket name for synthetic/sample documents."
  type        = string
}

variable "availability_zones" {
  description = "Availability zones used by the dev scaffold."
  type        = list(string)
}

variable "vpc_cidr" {
  description = "VPC CIDR block."
  type        = string
  default     = "10.40.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks."
  type        = list(string)
  default     = ["10.40.0.0/24", "10.40.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks."
  type        = list(string)
  default     = ["10.40.10.0/24", "10.40.11.0/24"]
}

variable "api_desired_count" {
  description = "Desired API task count."
  type        = number
  default     = 1
}

variable "embedding_provider" {
  description = "Default embedding provider."
  type        = string
  default     = "deterministic"
}

variable "answer_provider" {
  description = "Default answer provider."
  type        = string
  default     = "deterministic"
}

variable "db_name" {
  description = "Database name."
  type        = string
  default     = "enterprise_ai_agent"
}

variable "db_username" {
  description = "Database admin username. Password is managed by RDS, not Terraform variables."
  type        = string
  default     = "app_admin"
}

variable "db_instance_class" {
  description = "Development RDS instance class. Review cost before using."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage_gb" {
  description = "Development RDS storage size in GB."
  type        = number
  default     = 20
}

variable "postgres_engine_version" {
  description = "PostgreSQL engine version for RDS."
  type        = string
  default     = "16.4"
}

variable "rds_deletion_protection" {
  description = "Enable RDS deletion protection. Dev default is cleanup-friendly; production should use true."
  type        = bool
  default     = false
}

variable "rds_skip_final_snapshot" {
  description = "Skip final snapshot on deletion. Dev default is cleanup-friendly; production should use false."
  type        = bool
  default     = true
}

variable "rds_backup_retention_period" {
  description = "RDS automated backup retention in days. Dev default is low cost; production should use a reviewed value."
  type        = number
  default     = 1
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 30
}
