output "bucket_name" {
  description = "S3 bucket name for synthetic documents."
  value       = aws_s3_bucket.documents.bucket
}

output "bucket_arn" {
  description = "S3 bucket ARN."
  value       = aws_s3_bucket.documents.arn
}

output "read_policy_json" {
  description = "Least-privilege read policy JSON for ECS task roles."
  value       = data.aws_iam_policy_document.read_documents.json
}
