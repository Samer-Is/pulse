# Main Terraform configuration
# Orchestrates all modules

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# ECR Module
module "ecr" {
  source = "./modules/ecr"
  
  project_name = var.project_name
  environment  = var.environment
  
  repositories = ["frontend", "backend", "gateway", "worker"]
}

# IAM Module (OIDC for GitHub Actions)
module "iam" {
  source = "./modules/iam"
  
  project_name = var.project_name
  environment  = var.environment
  github_org   = var.github_org
  github_repo  = var.github_repo
  aws_region   = var.aws_region
}

# S3 Module
module "s3" {
  source = "./modules/s3"
  
  project_name = var.project_name
  environment  = var.environment
}

# Secrets Manager Module
module "secrets" {
  source = "./modules/secrets"
  
  project_name = var.project_name
  environment  = var.environment
}

# RDS Module
module "rds" {
  source = "./modules/rds"
  
  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  db_name           = var.db_name
  min_capacity      = var.db_min_capacity
  max_capacity      = var.db_max_capacity
  
  depends_on = [module.vpc]
}

# Redis Module
module "redis" {
  source = "./modules/redis"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  
  depends_on = [module.vpc]
}

# ALB Module
module "alb" {
  source = "./modules/alb"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  certificate_arn    = var.domain_name != "" ? module.acm[0].certificate_arn : ""
  
  depends_on = [module.vpc]
}

# ECS Module
module "ecs" {
  source = "./modules/ecs"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  
  alb_target_group_frontend_arn = module.alb.target_group_frontend_arn
  alb_target_group_backend_arn  = module.alb.target_group_backend_arn
  alb_target_group_gateway_arn  = module.alb.target_group_gateway_arn
  
  ecr_repositories = module.ecr.repository_urls
  
  frontend_cpu    = var.ecs_frontend_cpu
  frontend_memory = var.ecs_frontend_memory
  backend_cpu     = var.ecs_backend_cpu
  backend_memory  = var.ecs_backend_memory
  gateway_cpu     = var.ecs_gateway_cpu
  gateway_memory  = var.ecs_gateway_memory
  worker_cpu      = var.ecs_worker_cpu
  worker_memory   = var.ecs_worker_memory
  
  depends_on = [module.vpc, module.alb, module.ecr]
}

# SES Module
module "ses" {
  source = "./modules/ses"
  
  project_name = var.project_name
  environment  = var.environment
  domain_name  = var.domain_name
}

# ACM Module (optional, if domain provided)
module "acm" {
  count  = var.domain_name != "" ? 1 : 0
  source = "./modules/acm"
  
  project_name    = var.project_name
  environment     = var.environment
  domain_name     = var.domain_name
  hosted_zone_id  = var.hosted_zone_id
}

# CloudFront Module (optional)
module "cloudfront" {
  count  = var.domain_name != "" ? 1 : 0
  source = "./modules/cloudfront"
  
  project_name    = var.project_name
  environment     = var.environment
  alb_domain_name = module.alb.alb_dns_name
  certificate_arn = module.acm[0].certificate_arn_us_east_1
  domain_name     = var.domain_name
  
  depends_on = [module.alb, module.acm]
}

# Route53 Module (optional)
module "route53" {
  count  = var.domain_name != "" ? 1 : 0
  source = "./modules/route53"
  
  project_name        = var.project_name
  environment         = var.environment
  domain_name         = var.domain_name
  hosted_zone_id      = var.hosted_zone_id
  cloudfront_domain   = module.cloudfront[0].cloudfront_domain_name
  cloudfront_zone_id  = module.cloudfront[0].cloudfront_hosted_zone_id
  
  depends_on = [module.cloudfront]
}

# Observability Module
module "observability" {
  source = "./modules/observability"
  
  project_name = var.project_name
  environment  = var.environment
  
  alb_arn            = module.alb.alb_arn
  ecs_cluster_name   = module.ecs.cluster_name
  rds_cluster_id     = module.rds.cluster_id
  redis_cluster_id   = module.redis.cluster_id
  
  depends_on = [module.ecs, module.rds, module.redis]
}
