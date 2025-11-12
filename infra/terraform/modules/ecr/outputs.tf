# ECR Module Outputs

output "repository_urls" {
  description = "URLs of ECR repositories"
  value = {
    for k, v in aws_ecr_repository.repos : k => v.repository_url
  }
}

output "repository_arns" {
  description = "ARNs of ECR repositories"
  value = {
    for k, v in aws_ecr_repository.repos : k => v.arn
  }
}

output "registry_id" {
  description = "Registry ID"
  value       = values(aws_ecr_repository.repos)[0].registry_id
}

