# RDS Module - Aurora PostgreSQL Serverless v2

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
resource "random_password" "master" {
  length  = 32
  special = true
}

# Aurora Cluster
resource "aws_rds_cluster" "main" {
  cluster_identifier      = "${local.name_prefix}-aurora-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.4"
  database_name           = var.db_name
  master_username         = "pulseadmin"
  master_password         = random_password.master.result
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [var.rds_security_group_id]
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  skip_final_snapshot     = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${local.name_prefix}-final-snapshot" : null
  
  serverlessv2_scaling_configuration {
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
  }

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    Name = "${local.name_prefix}-aurora-cluster"
  }
}

# Aurora Instance (Serverless v2)
resource "aws_rds_cluster_instance" "main" {
  identifier         = "${local.name_prefix}-aurora-instance-1"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version

  tags = {
    Name = "${local.name_prefix}-aurora-instance-1"
  }
}

# Store database URL in Secrets Manager
resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = "AI_STUDIO_DATABASE_URL"
  secret_string = "postgresql://${aws_rds_cluster.main.master_username}:${random_password.master.result}@${aws_rds_cluster.main.endpoint}:5432/${aws_rds_cluster.main.database_name}"

  depends_on = [aws_rds_cluster.main]
}

