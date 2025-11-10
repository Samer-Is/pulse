variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "domain_name" {
  description = "Primary domain name"
  type        = string
  default     = ""
}

variable "alternative_names" {
  description = "Alternative domain names (SANs)"
  type        = list(string)
  default     = []
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for DNS validation (optional)"
  type        = string
  default     = ""
}

