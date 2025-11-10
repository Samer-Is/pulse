output "certificate_arn" {
  description = "ARN of ACM certificate"
  value       = var.domain_name != "" ? aws_acm_certificate.main[0].arn : null
}

output "certificate_domain" {
  description = "Domain name of certificate"
  value       = var.domain_name != "" ? aws_acm_certificate.main[0].domain_name : null
}

output "certificate_status" {
  description = "Status of certificate"
  value       = var.domain_name != "" ? aws_acm_certificate.main[0].status : null
}

