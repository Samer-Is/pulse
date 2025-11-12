# ECR Module Variables

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "max_image_count" {
  description = "Maximum number of images to retain per repository"
  type        = number
  default     = 10
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

