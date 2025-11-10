output "secret_arns" {
  description = "Map of secret names to ARNs"
  value       = { for k, v in aws_secretsmanager_secret.secrets : k => v.arn }
}

output "secret_names" {
  description = "List of secret names"
  value       = keys(aws_secretsmanager_secret.secrets)
}

