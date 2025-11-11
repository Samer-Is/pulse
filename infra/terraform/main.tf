# Main Terraform configuration
# Orchestrates all modules with proper dependency order

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ==============================================================================
# PHASE 1: Foundation (No dependencies)
# ==============================================================================

# VPC Module (creates VPC, subnets, NAT, security groups)
module "vpc" {
  source = "./modules/vpc"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# S3 Module (creates buckets)
module "s3" {
  source = "./modules/s3"
  
  project_name = var.project_name
  environment  = var.environment
}

# IAM Module (creates roles for GitHub OIDC and ECS)
module "iam" {
  source = "./modules/iam"
  
  project_name = var.project_name
  environment  = var.environment
  github_org   = var.github_org
  github_repo  = var.github_repo
  aws_region   = var.aws_region
}

# ECR Module (creates container registries)
module "ecr" {
  source = "./modules/ecr"
  
  project_name = var.project_name
  environment  = var.environment
  
  repositories = ["frontend", "backend", "gateway", "worker"]
}

# ==============================================================================
# PHASE 2: Dependent Infrastructure
# ==============================================================================

# Secrets Manager Module (needs S3 bucket names)
module "secrets" {
  source = "./modules/secrets"
  
  project_name           = var.project_name
  environment            = var.environment
  aws_region             = var.aws_region
  assets_bucket_name     = module.s3.assets_bucket_name
  quarantine_bucket_name = module.s3.quarantine_bucket_name
  
  depends_on = [module.s3]
}

# RDS Module (needs VPC and security groups)
# Using Free Tier PostgreSQL (db.t3.micro)
module "rds" {
  source = "./modules/rds"
  
  project_name           = var.project_name
  environment            = var.environment
  vpc_id                 = module.vpc.vpc_id
  private_subnet_ids     = module.vpc.private_subnet_ids
  rds_security_group_id  = module.vpc.rds_security_group_id
  db_name                = var.db_name
  
  depends_on = [module.vpc]
}

# Redis Module (needs VPC and security groups)
module "redis" {
  source = "./modules/redis"
  
  project_name             = var.project_name
  environment              = var.environment
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  redis_security_group_id  = module.vpc.redis_security_group_id
  
  depends_on = [module.vpc]
}

# ALB Module (needs VPC and security groups)
module "alb" {
  source = "./modules/alb"
  
  project_name            = var.project_name
  environment             = var.environment
  vpc_id                  = module.vpc.vpc_id
  public_subnet_ids       = module.vpc.public_subnet_ids
  alb_security_group_id   = module.vpc.alb_security_group_id
  certificate_arn         = ""  # No certificate for now
  
  depends_on = [module.vpc]
}

# SES Module (for sending emails)
module "ses" {
  source = "./modules/ses"
  
  project_name = var.project_name
  environment  = var.environment
  domain_name  = var.domain_name
}

# ==============================================================================
# PHASE 3: Observability (creates log groups for ECS)
# ==============================================================================

module "observability" {
  source = "./modules/observability"
  
  project_name = var.project_name
  environment  = var.environment
  
  alb_arn            = module.alb.alb_arn
  ecs_cluster_name   = "${var.project_name}-${var.environment}"  # Will be created by ECS module
  rds_cluster_id     = module.rds.cluster_id
  redis_cluster_id   = module.redis.cluster_id
  
  depends_on = [module.alb, module.rds, module.redis]
}

# ==============================================================================
# PHASE 4: ECS (needs everything else)
# ==============================================================================

module "ecs" {
  source = "./modules/ecs"
  
  # Basic config
  project_name    = var.project_name
  environment     = var.environment
  aws_region      = var.aws_region
  aws_account_id  = var.aws_account_id
  
  # Network
  vpc_id                  = module.vpc.vpc_id
  private_subnet_ids      = module.vpc.private_subnet_ids
  ecs_security_group_id   = module.vpc.ecs_tasks_security_group_id
  
  # IAM (matching exact variable names from ECS module)
  execution_role_arn = module.iam.ecs_task_execution_role_arn
  task_role_arn      = module.iam.ecs_task_role_arn
  
  # ALB (matching exact variable names)
  frontend_target_group_arn = module.alb.target_group_frontend_arn
  backend_target_group_arn  = module.alb.target_group_backend_arn
  gateway_target_group_arn  = module.alb.target_group_gateway_arn
  alb_listener_arn          = module.alb.http_listener_arn
  
  # CloudWatch Log Groups (matching exact variable names)
  log_group_frontend = module.observability.log_group_frontend
  log_group_backend  = module.observability.log_group_backend
  log_group_gateway  = module.observability.log_group_gateway
  log_group_worker   = module.observability.log_group_worker
  
  # ECR Repositories (as a map - matching exact variable name)
  ecr_repository_urls = module.ecr.repository_urls
  
  depends_on = [
    module.vpc,
    module.iam,
    module.alb,
    module.observability,
    module.ecr
  ]
}

# ==============================================================================
# OPTIONAL MODULES (Disabled for core infrastructure deployment)
# ==============================================================================

# ACM Module - DISABLED
# module "acm" {
#   count  = var.domain_name != "" ? 1 : 0
#   source = "./modules/acm"
#   
#   project_name    = var.project_name
#   environment     = var.environment
#   domain_name     = var.domain_name
#   hosted_zone_id  = var.hosted_zone_id
# }

# CloudFront Module - DISABLED
# module "cloudfront" {
#   count  = var.domain_name != "" ? 1 : 0
#   source = "./modules/cloudfront"
#   
#   project_name    = var.project_name
#   environment     = var.environment
#   alb_domain_name = module.alb.alb_dns_name
#   certificate_arn = module.acm[0].certificate_arn_us_east_1
#   domain_name     = var.domain_name
#   
#   depends_on = [module.alb, module.acm]
# }

# Route53 Module - DISABLED
# module "route53" {
#   count  = var.domain_name != "" ? 1 : 0
#   source = "./modules/route53"
#   
#   project_name        = var.project_name
#   environment         = var.environment
#   domain_name         = var.domain_name
#   hosted_zone_id      = var.hosted_zone_id
#   cloudfront_domain   = module.cloudfront[0].cloudfront_domain_name
#   cloudfront_zone_id  = module.cloudfront[0].cloudfront_hosted_zone_id
#   
#   depends_on = [module.cloudfront]
# }
