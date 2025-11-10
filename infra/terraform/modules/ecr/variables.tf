variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "repositories" {
  description = "List of repository names"
  type        = list(string)
  default     = ["frontend", "backend", "gateway", "worker"]
}

