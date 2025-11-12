# S3 Module Variables

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, prod)"
  type        = string
}

variable "enable_versioning" {
  description = "Enable S3 versioning"
  type        = bool
  default     = false
}

variable "object_expiration_days" {
  description = "Days after which objects expire"
  type        = number
  default     = 90
}

variable "allowed_origins" {
  description = "Allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

