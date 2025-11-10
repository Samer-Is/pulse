variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "alb_arn" {
  description = "ARN of the Application Load Balancer"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name of ECS cluster"
  type        = string
}

variable "rds_cluster_id" {
  description = "ID of RDS cluster"
  type        = string
}

variable "redis_cluster_id" {
  description = "ID of Redis cluster"
  type        = string
}

