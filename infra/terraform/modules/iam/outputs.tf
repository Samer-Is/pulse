output "github_oidc_provider_arn" {
  description = "ARN of GitHub OIDC provider"
  value       = aws_iam_openid_connect_provider.github.arn
}

output "github_oidc_role_infra_arn" {
  description = "ARN of GitHub Actions role for infrastructure (Terraform)"
  value       = aws_iam_role.github_actions_infra.arn
}

output "github_oidc_role_deploy_arn" {
  description = "ARN of GitHub Actions role for deployment (ECR/ECS)"
  value       = aws_iam_role.github_actions_deploy.arn
}

output "ecs_task_execution_role_arn" {
  description = "ARN of ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of ECS task role (application permissions)"
  value       = aws_iam_role.ecs_task.arn
}

