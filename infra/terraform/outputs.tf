# Terraform Outputs

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "alb_url" {
  description = "ALB URL"
  value       = "https://${module.alb.alb_dns_name}"
}

output "ecr_repositories" {
  description = "ECR repository URLs"
  value       = module.ecr.repository_urls
}

output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = module.ecs.cluster_name
}

output "rds_endpoint" {
  description = "RDS cluster endpoint"
  value       = module.rds.cluster_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.redis.endpoint
  sensitive   = true
}

output "s3_assets_bucket" {
  description = "S3 assets bucket name"
  value       = module.s3.assets_bucket_name
}

output "s3_tfstate_bucket" {
  description = "S3 Terraform state bucket"
  value       = module.s3.tfstate_bucket_name
}

# CloudFront disabled for core infrastructure deployment
# output "cloudfront_domain" {
#   description = "CloudFront domain name"
#   value       = var.domain_name != "" ? module.cloudfront[0].cloudfront_domain_name : "N/A (domain not configured)"
# }

output "github_oidc_role_arn_infra" {
  description = "GitHub Actions OIDC role ARN for infrastructure"
  value       = module.iam.github_oidc_role_infra_arn
}

output "github_oidc_role_arn_deploy" {
  description = "GitHub Actions OIDC role ARN for deployment"
  value       = module.iam.github_oidc_role_deploy_arn
}

output "ses_smtp_username" {
  description = "SES SMTP username"
  value       = module.ses.smtp_username
  sensitive   = true
}
