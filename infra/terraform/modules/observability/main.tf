locals {
  name_prefix = "${var.app_name}-${var.environment}"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/${local.name_prefix}/operations"
  retention_in_days = var.log_retention_days

  tags = {
    Application = var.app_name
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "evals" {
  name              = "/${local.name_prefix}/evals"
  retention_in_days = var.log_retention_days

  tags = {
    Application = var.app_name
    Environment = var.environment
  }
}

resource "aws_cloudwatch_dashboard" "operations" {
  count          = var.create_dashboard ? 1 : 0
  dashboard_name = "${local.name_prefix}-operations"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 3
        properties = {
          markdown = "Track request count, latency, model_call latency, token usage, eval status, and guardrail blocked count. Wire concrete metrics after production instrumentation is finalized."
        }
      }
    ]
  })
}
