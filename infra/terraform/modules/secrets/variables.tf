# Secrets Manager Module Variables

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of S3 bucket to store in secrets"
  type        = string
  default     = ""
}

variable "sqs_queue_url" {
  description = "URL of SQS queue to store in secrets"
  type        = string
  default     = ""
}

variable "database_connection_string" {
  description = "Database connection string"
  type        = string
  default     = ""
  sensitive   = true
}

variable "recovery_window_days" {
  description = "Number of days to retain deleted secrets"
  type        = number
  default     = 7
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

