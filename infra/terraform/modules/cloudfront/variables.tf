variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "alb_dns_name" {
  description = "ALB DNS name"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name for static assets (optional)"
  type        = string
  default     = ""
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "certificate_arn" {
  description = "ACM certificate ARN (optional)"
  type        = string
  default     = ""
}

variable "domain_aliases" {
  description = "List of domain aliases (CNAMEs)"
  type        = list(string)
  default     = []
}

variable "price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100" # US, Canada, Europe
}

