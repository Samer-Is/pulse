# Secrets Manager Module for Pulse AI Studio
# Creates placeholder secrets (to be filled manually after deployment)

terraform {
  required_version = ">= 1.6.0"
}

# List of secrets to create
locals {
  secrets = {
    "database-url"              = ""
    "s3-bucket-name"           = var.s3_bucket_name
    "sqs-queue-url"            = var.sqs_queue_url
    "jwt-secret"               = random_password.jwt_secret.result
    "openai-api-key"           = ""
    "anthropic-api-key"        = ""
    "google-oauth-client-id"   = ""
    "google-oauth-client-secret" = ""
    "gcp-vertex-project-id"    = ""
    "gcp-vertex-location"      = "us-central1"
    "gcp-vertex-sa-json"       = ""
    "runway-api-key"           = ""
    "pika-api-key"             = ""
  }
}

# Generate JWT secret
resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# Create secrets
resource "aws_secretsmanager_secret" "secrets" {
  for_each = local.secrets

  name        = "${var.project_name}/${each.key}"
  description = "Secret for ${each.key}"

  recovery_window_in_days = var.recovery_window_days

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${each.key}"
    }
  )
}

# Store secret values
resource "aws_secretsmanager_secret_version" "secrets" {
  for_each = local.secrets

  secret_id     = aws_secretsmanager_secret.secrets[each.key].id
  secret_string = each.value
}

# Database URL secret (updated after RDS creation)
resource "aws_secretsmanager_secret_version" "database_url" {
  count = var.database_connection_string != "" ? 1 : 0

  secret_id     = aws_secretsmanager_secret.secrets["database-url"].id
  secret_string = var.database_connection_string

  lifecycle {
    ignore_changes = [secret_string]
  }
}

