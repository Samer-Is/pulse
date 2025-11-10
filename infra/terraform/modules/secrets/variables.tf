variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "assets_bucket_name" {
  description = "Name of assets S3 bucket"
  type        = string
}

variable "quarantine_bucket_name" {
  description = "Name of quarantine S3 bucket"
  type        = string
}

