# SQS Module Variables

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, prod)"
  type        = string
}

variable "visibility_timeout" {
  description = "Visibility timeout in seconds"
  type        = number
  default     = 300  # 5 minutes for video jobs
}

variable "message_retention" {
  description = "Message retention in seconds"
  type        = number
  default     = 345600  # 4 days
}

variable "max_receive_count" {
  description = "Max receive count before moving to DLQ"
  type        = number
  default     = 3
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

