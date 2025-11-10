output "record_name" {
  description = "DNS record name"
  value       = var.domain_name
}

output "record_type" {
  description = "DNS record type"
  value       = var.cloudfront_domain_name != "" ? "A (CloudFront)" : "A (ALB)"
}

