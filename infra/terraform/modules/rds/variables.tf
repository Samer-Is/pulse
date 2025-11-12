# RDS Module Variables

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "16.1"
}

variable "allocated_storage" {
  description = "Initial storage in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage for autoscaling in GB"
  type        = number
  default     = 100
}

variable "database_name" {
  description = "Name of the database"
  type        = string
  default     = "pulse"
}

variable "master_username" {
  description = "Master username for database"
  type        = string
  default     = "pulse_admin"
}

variable "db_subnet_group_name" {
  description = "Name of DB subnet group"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID for RDS"
  type        = string
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on deletion (set to false in production)"
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

