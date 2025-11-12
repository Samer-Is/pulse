# Dev Environment Variables

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "pulse"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

# VPC Variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["eu-central-1a", "eu-central-1b"]
}

variable "ssh_allowed_ips" {
  description = "IP addresses allowed to SSH (set to your IP in production)"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # CHANGE THIS IN PRODUCTION!
}

# EC2 Variables
variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# RDS Variables
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "16.1"
}

variable "rds_allocated_storage" {
  description = "Initial RDS storage in GB"
  type        = number
  default     = 20
}

variable "database_name" {
  description = "Database name"
  type        = string
  default     = "pulse"
}

variable "database_username" {
  description = "Database master username"
  type        = string
  default     = "pulse_admin"
}

variable "skip_final_snapshot" {
  description = "Skip final DB snapshot on destroy (dev only)"
  type        = bool
  default     = true  # Set to false in production
}

variable "deletion_protection" {
  description = "Enable RDS deletion protection"
  type        = bool
  default     = false  # Set to true in production
}

# S3 Variables
variable "cors_allowed_origins" {
  description = "CORS allowed origins for S3"
  type        = list(string)
  default     = ["*"]  # Restrict in production
}

