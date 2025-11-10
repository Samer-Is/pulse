output "domain_identity_arn" {
  description = "ARN of SES domain identity"
  value       = var.domain_name != "" ? aws_ses_domain_identity.main[0].arn : null
}

output "dkim_tokens" {
  description = "DKIM tokens for DNS configuration"
  value       = var.domain_name != "" ? aws_ses_domain_dkim.main[0].dkim_tokens : []
}

output "email_identity_arn" {
  description = "ARN of email identity"
  value       = aws_ses_email_identity.noreply.arn
}

output "configuration_set_name" {
  description = "Name of SES configuration set"
  value       = aws_ses_configuration_set.main.name
}

output "smtp_username" {
  description = "SMTP username (use IAM user credentials)"
  value       = "Use IAM credentials for SMTP"
}

