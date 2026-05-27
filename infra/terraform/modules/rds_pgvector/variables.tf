variable "app_name" {
  description = "Application name used in resource names."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for the database security group."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for the database subnet group."
  type        = list(string)
}

variable "app_security_group_id" {
  description = "Security group ID allowed to connect to PostgreSQL."
  type        = string
}

variable "db_name" {
  description = "Initial database name."
  type        = string
}

variable "db_username" {
  description = "Database admin username. Password is managed by RDS Secrets Manager integration."
  type        = string
}

variable "db_instance_class" {
  description = "RDS instance class for the dev scaffold."
  type        = string
}

variable "allocated_storage_gb" {
  description = "Allocated storage in GB."
  type        = number
}

variable "engine_version" {
  description = "PostgreSQL engine version."
  type        = string
}

variable "deletion_protection" {
  description = "Whether RDS deletion protection is enabled. Prefer true outside disposable dev environments."
  type        = bool
}

variable "skip_final_snapshot" {
  description = "Whether to skip a final DB snapshot on deletion. Dev may use true; production should use false."
  type        = bool
}

variable "backup_retention_period" {
  description = "RDS automated backup retention in days. Use higher values outside dev."
  type        = number
}
