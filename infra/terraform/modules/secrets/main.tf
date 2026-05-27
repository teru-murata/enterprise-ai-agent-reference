resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = var.openai_api_key_secret_name
  description             = "Secret container for OPENAI_API_KEY. The value is intentionally not managed in Terraform state."
  recovery_window_in_days = 7

  tags = {
    Application = var.app_name
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret" "database_url" {
  name                    = var.database_url_secret_name
  description             = "Secret container for DATABASE_URL. The value is intentionally not managed in Terraform state."
  recovery_window_in_days = 7

  tags = {
    Application = var.app_name
    Environment = var.environment
  }
}
