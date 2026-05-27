variable "app_name" {
  description = "Application name used in resource names."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 30
}

variable "create_dashboard" {
  description = "Whether to create the placeholder CloudWatch dashboard."
  type        = bool
  default     = false
}
