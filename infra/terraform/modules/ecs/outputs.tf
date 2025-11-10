output "cluster_id" {
  description = "ECS cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

output "frontend_service_name" {
  description = "Frontend service name"
  value       = aws_ecs_service.frontend.name
}

output "backend_service_name" {
  description = "Backend service name"
  value       = aws_ecs_service.backend.name
}

output "gateway_service_name" {
  description = "Gateway service name"
  value       = aws_ecs_service.gateway.name
}

output "worker_service_name" {
  description = "Worker service name"
  value       = aws_ecs_service.worker.name
}

output "task_definition_arns" {
  description = "Map of service names to task definition ARNs"
  value = {
    frontend = aws_ecs_task_definition.frontend.arn
    backend  = aws_ecs_task_definition.backend.arn
    gateway  = aws_ecs_task_definition.gateway.arn
    worker   = aws_ecs_task_definition.worker.arn
  }
}

