output "api_log_group_name" {
  description = "API CloudWatch log group name."
  value       = aws_cloudwatch_log_group.api.name
}

output "evals_log_group_name" {
  description = "Evaluation CloudWatch log group name."
  value       = aws_cloudwatch_log_group.evals.name
}
