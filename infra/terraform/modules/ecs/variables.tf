variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  type        = string
}

variable "execution_role_arn" {
  description = "ECS task execution role ARN"
  type        = string
}

variable "task_role_arn" {
  description = "ECS task role ARN (application permissions)"
  type        = string
}

variable "ecr_repository_urls" {
  description = "Map of service names to ECR repository URLs"
  type        = map(string)
}

variable "frontend_target_group_arn" {
  description = "Frontend target group ARN"
  type        = string
}

variable "backend_target_group_arn" {
  description = "Backend target group ARN"
  type        = string
}

variable "gateway_target_group_arn" {
  description = "Gateway target group ARN"
  type        = string
}

variable "alb_listener_arn" {
  description = "ALB listener ARN (for dependency)"
  type        = string
}

variable "log_group_frontend" {
  description = "CloudWatch log group for frontend"
  type        = string
}

variable "log_group_backend" {
  description = "CloudWatch log group for backend"
  type        = string
}

variable "log_group_gateway" {
  description = "CloudWatch log group for gateway"
  type        = string
}

variable "log_group_worker" {
  description = "CloudWatch log group for worker"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "api_base_url" {
  description = "Backend API base URL"
  type        = string
  default     = "http://localhost:8080/v1"
}

variable "gateway_base_url" {
  description = "Gateway API base URL"
  type        = string
  default     = "http://localhost:8081/v1"
}

variable "frontend_desired_count" {
  description = "Desired count of frontend tasks"
  type        = number
  default     = 2
}

variable "backend_desired_count" {
  description = "Desired count of backend tasks"
  type        = number
  default     = 2
}

variable "gateway_desired_count" {
  description = "Desired count of gateway tasks"
  type        = number
  default     = 2
}

variable "worker_desired_count" {
  description = "Desired count of worker tasks"
  type        = number
  default     = 1
}

