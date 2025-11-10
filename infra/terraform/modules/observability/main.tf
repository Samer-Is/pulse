# Observability Module - CloudWatch Logs, X-Ray, Alarms

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "ecs_frontend" {
  name              = "/ecs/${local.name_prefix}/frontend"
  retention_in_days = 30

  tags = {
    Name = "${local.name_prefix}-frontend-logs"
  }
}

resource "aws_cloudwatch_log_group" "ecs_backend" {
  name              = "/ecs/${local.name_prefix}/backend"
  retention_in_days = 30

  tags = {
    Name = "${local.name_prefix}-backend-logs"
  }
}

resource "aws_cloudwatch_log_group" "ecs_gateway" {
  name              = "/ecs/${local.name_prefix}/gateway"
  retention_in_days = 30

  tags = {
    Name = "${local.name_prefix}-gateway-logs"
  }
}

resource "aws_cloudwatch_log_group" "ecs_worker" {
  name              = "/ecs/${local.name_prefix}/worker"
  retention_in_days = 30

  tags = {
    Name = "${local.name_prefix}-worker-logs"
  }
}

# CloudWatch Alarms - ALB
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${local.name_prefix}-alb-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "ALB 5xx errors exceeded threshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = var.alb_arn
  }

  tags = {
    Name = "${local.name_prefix}-alb-5xx-alarm"
  }
}

# CloudWatch Alarms - ECS
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${local.name_prefix}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization is too high"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ClusterName = var.ecs_cluster_name
  }

  tags = {
    Name = "${local.name_prefix}-ecs-cpu-alarm"
  }
}

# CloudWatch Alarms - RDS
resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${local.name_prefix}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU utilization is too high"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBClusterIdentifier = var.rds_cluster_id
  }

  tags = {
    Name = "${local.name_prefix}-rds-cpu-alarm"
  }
}

# CloudWatch Alarms - Redis
resource "aws_cloudwatch_metric_alarm" "redis_cpu_high" {
  alarm_name          = "${local.name_prefix}-redis-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Redis CPU utilization is too high"
  treat_missing_data  = "notBreaching"

  dimensions = {
    CacheClusterId = var.redis_cluster_id
  }

  tags = {
    Name = "${local.name_prefix}-redis-cpu-alarm"
  }
}

# X-Ray Sampling Rule
resource "aws_xray_sampling_rule" "main" {
  rule_name      = "${local.name_prefix}-sampling-rule"
  priority       = 1000
  version        = 1
  reservoir_size = 1
  fixed_rate     = 0.05
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "*"
  resource_arn   = "*"

  tags = {
    Name = "${local.name_prefix}-xray-sampling"
  }
}

