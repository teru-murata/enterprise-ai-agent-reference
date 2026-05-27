variable "app_name" {
  description = "Application name used in resource names."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR range for the VPC."
  type        = string
}

variable "public_subnet_cidrs" {
  description = "CIDR ranges for public subnets."
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR ranges for private subnets."
  type        = list(string)
}

variable "availability_zones" {
  description = "Availability zones to use for subnets."
  type        = list(string)
}
