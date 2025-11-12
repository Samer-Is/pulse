# Pulse AI Studio - Dev Environment
# Main Terraform configuration for development environment

terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Backend for state storage (optional - uncomment after S3 bucket creation)
  # backend "s3" {
  #   bucket = "pulse-terraform-state"
  #   key    = "dev/terraform.tfstate"
  #   region = "eu-central-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Local variables
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name        = var.project_name
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  ssh_allowed_ips     = var.ssh_allowed_ips
  tags                = local.common_tags
}

# RDS Module
module "rds" {
  source = "../../modules/rds"

  project_name           = var.project_name
  instance_class         = var.rds_instance_class
  postgres_version       = var.postgres_version
  allocated_storage      = var.rds_allocated_storage
  database_name          = var.database_name
  master_username        = var.database_username
  db_subnet_group_name   = module.vpc.db_subnet_group_name
  security_group_id      = module.vpc.rds_security_group_id
  backup_retention_days  = 7
  skip_final_snapshot    = var.skip_final_snapshot
  deletion_protection    = var.deletion_protection
  tags                   = local.common_tags
}

# S3 Module
module "s3" {
  source = "../../modules/s3"

  project_name           = var.project_name
  environment            = var.environment
  enable_versioning      = false
  object_expiration_days = 90
  allowed_origins        = var.cors_allowed_origins
  tags                   = local.common_tags
}

# SQS Module
module "sqs" {
  source = "../../modules/sqs"

  project_name       = var.project_name
  environment        = var.environment
  visibility_timeout = 300
  message_retention  = 345600
  max_receive_count  = 3
  tags               = local.common_tags
}

# ECR Module
module "ecr" {
  source = "../../modules/ecr"

  project_name    = var.project_name
  max_image_count = 10
  tags            = local.common_tags
}

# Secrets Manager Module
module "secrets" {
  source = "../../modules/secrets"

  project_name                = var.project_name
  s3_bucket_name              = module.s3.bucket_name
  sqs_queue_url               = module.sqs.queue_url
  database_connection_string  = module.rds.connection_string
  recovery_window_days        = 7
  tags                        = local.common_tags
}

# EC2 Module (depends on other resources)
module "ec2" {
  source = "../../modules/ec2"

  project_name         = var.project_name
  instance_type        = var.ec2_instance_type
  subnet_id            = module.vpc.public_subnet_ids[0]
  security_group_id    = module.vpc.ec2_security_group_id
  root_volume_size     = 20
  aws_region           = var.aws_region
  s3_bucket_arn        = module.s3.bucket_arn
  sqs_queue_arn        = module.sqs.queue_arn
  secrets_arn_prefix   = module.secrets.secrets_arn_prefix
  tags                 = local.common_tags
}

