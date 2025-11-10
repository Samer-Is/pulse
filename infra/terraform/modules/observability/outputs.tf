output "log_group_frontend" {
  description = "Name of frontend log group"
  value       = aws_cloudwatch_log_group.ecs_frontend.name
}

output "log_group_backend" {
  description = "Name of backend log group"
  value       = aws_cloudwatch_log_group.ecs_backend.name
}

output "log_group_gateway" {
  description = "Name of gateway log group"
  value       = aws_cloudwatch_log_group.ecs_gateway.name
}

output "log_group_worker" {
  description = "Name of worker log group"
  value       = aws_cloudwatch_log_group.ecs_worker.name
}

output "alarm_arns" {
  description = "List of CloudWatch alarm ARNs"
  value = [
    aws_cloudwatch_metric_alarm.alb_5xx.arn,
    aws_cloudwatch_metric_alarm.ecs_cpu_high.arn,
    aws_cloudwatch_metric_alarm.rds_cpu_high.arn,
    aws_cloudwatch_metric_alarm.redis_cpu_high.arn
  ]
}

