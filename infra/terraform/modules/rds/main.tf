# RDS Module for Pulse AI Studio
# Creates db.t4g.micro PostgreSQL for cost optimization

terraform {
  required_version = ">= 1.6.0"
}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-postgres"

  # Engine
  engine         = "postgres"
  engine_version = var.postgres_version

  # Instance
  instance_class        = var.instance_class
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  # Database
  db_name  = var.database_name
  username = var.master_username
  password = random_password.db_password.result
  port     = 5432

  # Network
  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = [var.security_group_id]
  publicly_accessible    = false

  # Backup
  backup_retention_period = var.backup_retention_days
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"
  skip_final_snapshot     = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.rds_monitoring.arn

  # Performance
  performance_insights_enabled    = false  # Costs extra, disabled for budget
  auto_minor_version_upgrade      = true
  deletion_protection             = var.deletion_protection

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-rds"
    }
  )
}

# IAM Role for Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.project_name}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
  ]

  tags = var.tags
}

