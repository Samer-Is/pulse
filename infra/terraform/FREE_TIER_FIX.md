# AWS Free Tier Fix - RDS Aurora Not Available

## Problem
Aurora Serverless v2 is not available on AWS Free Tier accounts.

## ✅ Solution 1: Use Free Tier RDS PostgreSQL (RECOMMENDED FOR FREE TIER)

Replace Aurora with a free-tier-eligible RDS PostgreSQL instance.

### Update `infra/terraform/modules/rds/main.tf`:

Replace the entire content with:

```hcl
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-${var.environment}-postgres"
  engine         = "postgres"
  engine_version = "15.4"
  
  # Free Tier eligible
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  storage_type      = "gp2"
  
  db_name  = var.db_name
  username = "postgres"
  password = random_password.master.result
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.rds_security_group_id]
  
  publicly_accessible = false
  skip_final_snapshot = var.skip_final_snapshot
  
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  tags = {
    Name = "${var.project_name}-${var.environment}-postgres"
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids
  
  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

resource "random_password" "master" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret_version" "db_url" {
  secret_id = "AI_STUDIO_DATABASE_URL"
  secret_string = "postgresql://postgres:${random_password.master.result}@${aws_db_instance.main.endpoint}/${var.db_name}"
  
  depends_on = [aws_db_instance.main]
}
```

### Update `infra/terraform/modules/rds/variables.tf`:

Remove Aurora-specific variables (`min_capacity`, `max_capacity`).

### Update `infra/terraform/modules/rds/outputs.tf`:

```hcl
output "cluster_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "cluster_id" {
  description = "RDS instance identifier"
  value       = aws_db_instance.main.id
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}
```

### Update `infra/terraform/main.tf`:

```hcl
module "rds" {
  source = "./modules/rds"
  
  project_name           = var.project_name
  environment            = var.environment
  vpc_id                 = module.vpc.vpc_id
  private_subnet_ids     = module.vpc.private_subnet_ids
  rds_security_group_id  = module.vpc.rds_security_group_id
  db_name                = var.db_name
  skip_final_snapshot    = true  # Free tier
  
  depends_on = [module.vpc]
}
```

## ✅ Solution 2: Upgrade AWS Account (RECOMMENDED FOR PRODUCTION)

1. Go to AWS Billing Dashboard
2. Upgrade from Free Tier to Pay-As-You-Go
3. Re-run `terraform apply`

This will enable Aurora Serverless v2 with auto-scaling (0.5-1 ACU).

**Cost:** ~$0.12/hr when active (~$30-40/month with auto-pause)

## ✅ Solution 3: Use External Database

Use a managed PostgreSQL service:
- **Supabase** (Free tier: 500 MB)
- **Neon** (Free tier: 0.5 GB)
- **Railway** (Free trial: $5 credit)

Update secrets in AWS Secrets Manager with the external database URL.

## Next Steps

**If choosing Solution 1 (Free Tier RDS):**

```powershell
# 1. Update the RDS module files as shown above

# 2. Destroy the partially created RDS resources
cd C:\Users\s.ismail\Desktop\AI_STUDIO\infra\terraform
C:\terraform\terraform.exe destroy -target=module.rds -var-file="terraform.tfvars.optimized" -auto-approve

# 3. Re-deploy with free tier RDS
C:\terraform\terraform.exe apply -var-file="terraform.tfvars.optimized" -auto-approve
```

**If choosing Solution 2 (Upgrade AWS):**

1. Upgrade AWS account
2. Run: `terraform apply -var-file="terraform.tfvars.optimized" -auto-approve`

**If choosing Solution 3 (External DB):**

1. Create database on Supabase/Neon/Railway
2. Update AI_STUDIO_DATABASE_URL secret in AWS Secrets Manager
3. Skip RDS module deployment

---

**Current Infrastructure Cost (without RDS):** ~$20-30/month
**With Free Tier RDS:** ~$20-30/month (RDS free tier covers it)
**With Aurora Serverless v2:** ~$50-70/month

