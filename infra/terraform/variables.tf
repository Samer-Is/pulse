# Core variables
variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name (used for resource naming)"
  type        = string
  default     = "ai-studio"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# Domain & DNS (optional)
variable "domain_name" {
  description = "Domain name (e.g., pulse.ai). Leave empty to use ALB domain."
  type        = string
  default     = ""
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID. Required if domain_name is provided."
  type        = string
  default     = ""
}

# Network
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
}

# Database
variable "db_name" {
  description = "Database name"
  type        = string
  default     = "pulse_ai"
}

variable "db_min_capacity" {
  description = "Aurora Serverless v2 minimum ACUs"
  type        = number
  default     = 0.5
}

variable "db_max_capacity" {
  description = "Aurora Serverless v2 maximum ACUs"
  type        = number
  default     = 4
}

# ECS
variable "ecs_frontend_cpu" {
  description = "Frontend task CPU units"
  type        = number
  default     = 512
}

variable "ecs_frontend_memory" {
  description = "Frontend task memory (MB)"
  type        = number
  default     = 1024
}

variable "ecs_backend_cpu" {
  description = "Backend task CPU units"
  type        = number
  default     = 1024
}

variable "ecs_backend_memory" {
  description = "Backend task memory (MB)"
  type        = number
  default     = 2048
}

variable "ecs_gateway_cpu" {
  description = "Gateway task CPU units"
  type        = number
  default     = 1024
}

variable "ecs_gateway_memory" {
  description = "Gateway task memory (MB)"
  type        = number
  default     = 2048
}

variable "ecs_worker_cpu" {
  description = "Worker task CPU units"
  type        = number
  default     = 512
}

variable "ecs_worker_memory" {
  description = "Worker task memory (MB)"
  type        = number
  default     = 1024
}

# GitHub Actions OIDC
variable "github_org" {
  description = "GitHub organization or username"
  type        = string
  default     = "your-github-org"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "ai-studio"
}
