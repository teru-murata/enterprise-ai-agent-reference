variable "app_name" {
  description = "Application name used in resource names."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name for synthetic documents."
  type        = string
}

variable "enable_versioning" {
  description = "Whether to enable S3 object versioning."
  type        = bool
  default     = true
}
