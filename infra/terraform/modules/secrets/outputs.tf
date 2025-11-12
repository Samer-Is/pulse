# Secrets Manager Module Outputs

output "secret_arns" {
  description = "ARNs of all secrets"
  value = {
    for k, v in aws_secretsmanager_secret.secrets : k => v.arn
  }
}

output "secret_ids" {
  description = "IDs of all secrets"
  value = {
    for k, v in aws_secretsmanager_secret.secrets : k => v.id
  }
}

output "secrets_arn_prefix" {
  description = "ARN prefix for all secrets"
  value       = "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}/*"
}

output "jwt_secret" {
  description = "Generated JWT secret"
  value       = random_password.jwt_secret.result
  sensitive   = true
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

