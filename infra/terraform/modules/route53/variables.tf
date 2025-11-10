variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Domain name for A record"
  type        = string
  default     = ""
}

variable "cloudfront_domain_name" {
  description = "CloudFront distribution domain name (optional)"
  type        = string
  default     = ""
}

variable "cloudfront_zone_id" {
  description = "CloudFront distribution zone ID (optional)"
  type        = string
  default     = ""
}

variable "alb_dns_name" {
  description = "ALB DNS name (fallback if no CloudFront)"
  type        = string
  default     = ""
}

variable "alb_zone_id" {
  description = "ALB zone ID (fallback if no CloudFront)"
  type        = string
  default     = ""
}

