variable "app_name" {
  description = "Application name used in resource tags."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "repository_name" {
  description = "ECR repository name for the FastAPI API image."
  type        = string
}

variable "image_tag_mutability" {
  description = "ECR image tag mutability."
  type        = string
  default     = "MUTABLE"
}

variable "scan_on_push" {
  description = "Whether ECR scans images on push."
  type        = bool
  default     = true
}
