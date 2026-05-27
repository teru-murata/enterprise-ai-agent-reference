output "openai_api_key_secret_arn" {
  description = "ARN of the OpenAI API key secret container."
  value       = aws_secretsmanager_secret.openai_api_key.arn
}

output "database_url_secret_arn" {
  description = "ARN of the DATABASE_URL secret container."
  value       = aws_secretsmanager_secret.database_url.arn
}
