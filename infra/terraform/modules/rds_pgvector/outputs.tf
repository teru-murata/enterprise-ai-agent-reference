output "db_instance_endpoint" {
  description = "RDS endpoint for application configuration."
  value       = aws_db_instance.this.endpoint
}

output "db_security_group_id" {
  description = "Database security group ID."
  value       = aws_security_group.db.id
}

output "master_user_secret_arn" {
  description = "AWS-managed master user secret ARN."
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
}
