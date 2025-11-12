# SQS Module for Pulse AI Studio
# Creates queue for async jobs (video generation, etc.)

terraform {
  required_version = ">= 1.6.0"
}

# Main SQS Queue
resource "aws_sqs_queue" "main" {
  name                       = "${var.project_name}-${var.environment}-jobs"
  visibility_timeout_seconds = var.visibility_timeout
  message_retention_seconds  = var.message_retention
  max_message_size           = 262144  # 256 KB
  delay_seconds              = 0
  receive_wait_time_seconds  = 20  # Long polling

  # Dead Letter Queue configuration
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.max_receive_count
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-jobs-queue"
    }
  )
}

# Dead Letter Queue
resource "aws_sqs_queue" "dlq" {
  name                       = "${var.project_name}-${var.environment}-jobs-dlq"
  message_retention_seconds  = 1209600  # 14 days
  receive_wait_time_seconds  = 20

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-jobs-dlq"
    }
  )
}

# Queue policy (optional - for cross-account access)
resource "aws_sqs_queue_policy" "main" {
  queue_url = aws_sqs_queue.main.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowEC2Access"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.main.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# Current AWS account
data "aws_caller_identity" "current" {}

