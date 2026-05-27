variable "app_name" {
  description = "Application name used in resource names."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "openai_api_key_secret_name" {
  description = "Name for the OpenAI API key secret container. Secret value must be created out of band."
  type        = string
}

variable "database_url_secret_name" {
  description = "Name for the DATABASE_URL secret container. Secret value must be created out of band."
  type        = string
}
