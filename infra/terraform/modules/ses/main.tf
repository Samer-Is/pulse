# SES Module - Email configuration

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Email Identity (if domain provided)
resource "aws_ses_domain_identity" "main" {
  count  = var.domain_name != "" ? 1 : 0
  domain = var.domain_name
}

# DKIM tokens for domain
resource "aws_ses_domain_dkim" "main" {
  count  = var.domain_name != "" ? 1 : 0
  domain = aws_ses_domain_identity.main[0].domain
}

# Email address identity (for sandbox mode)
resource "aws_ses_email_identity" "noreply" {
  email = "noreply@${var.domain_name != "" ? var.domain_name : "example.com"}"
}

# Configuration Set
resource "aws_ses_configuration_set" "main" {
  name = "${local.name_prefix}-config-set"
}

# SNS topic for bounce/complaint notifications (optional)
resource "aws_sns_topic" "ses_notifications" {
  name = "${local.name_prefix}-ses-notifications"

  tags = {
    Name = "${local.name_prefix}-ses-notifications"
  }
}

# Event destination for bounces
resource "aws_ses_event_destination" "bounce" {
  name                   = "bounce-destination"
  configuration_set_name = aws_ses_configuration_set.main.name
  enabled                = true
  matching_types         = ["bounce", "complaint"]

  sns_destination {
    topic_arn = aws_sns_topic.ses_notifications.arn
  }
}

