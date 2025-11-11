# RDS Module - Free Tier PostgreSQL

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${local.name_prefix}-db-subnet-group"
  }
}

# Random password for master user
# RDS doesn't allow: / @ " ' space
resource "random_password" "master" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# RDS PostgreSQL Instance (Free Tier Eligible)
resource "aws_db_instance" "main" {
  identifier     = "${local.name_prefix}-postgres"
  engine         = "postgres"
  engine_version = "15"
  
  # Free Tier eligible configuration
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  storage_type      = "gp2"
  
  db_name  = var.db_name
  username = "pulseadmin"
  password = random_password.master.result
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.rds_security_group_id]
  
  publicly_accessible = false
  skip_final_snapshot = true  # For dev/test environments
  
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  # Performance Insights (optional, adds minimal cost)
  performance_insights_enabled = false
  
  # Auto minor version upgrade
  auto_minor_version_upgrade = true
  
  tags = {
    Name = "${local.name_prefix}-postgres"
  }
}

# Store database URL in Secrets Manager
resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = "AI_STUDIO_DATABASE_URL"
  secret_string = "postgresql://${aws_db_instance.main.username}:${random_password.master.result}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"

  depends_on = [aws_db_instance.main]
}
