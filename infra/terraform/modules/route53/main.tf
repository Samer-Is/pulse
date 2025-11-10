# Route53 Module - DNS records

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# A record pointing to CloudFront (if distribution provided)
resource "aws_route53_record" "cloudfront" {
  count = var.zone_id != "" && var.cloudfront_domain_name != "" && var.domain_name != "" ? 1 : 0

  zone_id = var.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_zone_id
    evaluate_target_health = false
  }
}

# AAAA record (IPv6) pointing to CloudFront
resource "aws_route53_record" "cloudfront_ipv6" {
  count = var.zone_id != "" && var.cloudfront_domain_name != "" && var.domain_name != "" ? 1 : 0

  zone_id = var.zone_id
  name    = var.domain_name
  type    = "AAAA"

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_zone_id
    evaluate_target_health = false
  }
}

# A record pointing directly to ALB (if no CloudFront)
resource "aws_route53_record" "alb" {
  count = var.zone_id != "" && var.cloudfront_domain_name == "" && var.alb_dns_name != "" && var.domain_name != "" ? 1 : 0

  zone_id = var.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

