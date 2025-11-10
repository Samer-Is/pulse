# Redis Module - ElastiCache Redis for caching and rate limiting

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${local.name_prefix}-redis-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${local.name_prefix}-redis-subnet-group"
  }
}

# Redis Cluster
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${local.name_prefix}-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [var.redis_security_group_id]

  tags = {
    Name = "${local.name_prefix}-redis"
  }
}

# Store Redis URL in Secrets Manager
resource "aws_secretsmanager_secret_version" "redis_url" {
  secret_id     = "AI_STUDIO_REDIS_URL"
  secret_string = "redis://${aws_elasticache_cluster.main.cache_nodes[0].address}:${aws_elasticache_cluster.main.cache_nodes[0].port}/0"

  depends_on = [aws_elasticache_cluster.main]
}

