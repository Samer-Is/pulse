# EC2 Module Variables

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "subnet_id" {
  description = "Subnet ID for EC2 instance"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID for EC2"
  type        = string
}

variable "root_volume_size" {
  description = "Size of root volume in GB"
  type        = number
  default     = 20
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of S3 bucket for permissions"
  type        = string
}

variable "sqs_queue_arn" {
  description = "ARN of SQS queue for permissions"
  type        = string
}

variable "secrets_arn_prefix" {
  description = "ARN prefix for Secrets Manager secrets"
  type        = string
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

