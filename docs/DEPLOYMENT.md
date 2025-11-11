# Pulse AI Studio - Deployment Guide

## Prerequisites

- AWS Account with admin access
- GitHub account
- Domain name (optional, can use ALB/CloudFront domains)
- Local tools: Terraform v1.5+, AWS CLI v2, Docker

---

## 1. AWS Setup

### 1.1 Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID, Secret Key, Region (eu-central-1), and output format (json)
```

### 1.2 Create S3 Backend for Terraform State

```bash
cd infra/terraform
terraform init
terraform apply -target=module.s3
```

---

## 2. GitHub OIDC Setup

### 2.1 Add GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions:

**Secrets:**
- `AWS_ACCOUNT_ID`: Your 12-digit AWS account ID

**Variables:**
- `AWS_REGION`: eu-central-1 (or your chosen region)

### 2.2 Deploy IAM OIDC Provider

```bash
terraform apply -target=module.iam
```

---

## 3. Infrastructure Deployment

### 3.1 Update terraform.tfvars

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
aws_account_id = "123456789012"
aws_region     = "eu-central-1"
project_name   = "pulse-ai"
domain_name    = "yourdomain.com"  # Optional
hosted_zone_id = "Z123456789ABC"   # Optional, if using Route53
```

### 3.2 Deploy All Infrastructure

```bash
terraform apply
```

This will create:
- VPC with 3 AZs
- RDS Aurora PostgreSQL Serverless v2
- ElastiCache Redis
- ECS Cluster (no services yet)
- S3 buckets
- ALB + Target Groups
- CloudWatch logs
- Secrets Manager entries

**⏱️ Expected time:** 15-20 minutes

---

## 4. Secrets Configuration

### 4.1 Add API Keys to Secrets Manager

```bash
aws secretsmanager put-secret-value \
  --secret-id OPENAI_API_KEY \
  --secret-string "sk-proj-..."

aws secretsmanager put-secret-value \
  --secret-id ANTHROPIC_API_KEY \
  --secret-string "sk-ant-..."

aws secretsmanager put-secret-value \
  --secret-id GOOGLE_API_KEY \
  --secret-string "AIza..."
```

### 4.2 Verify All Secrets

```bash
aws secretsmanager list-secrets --query 'SecretList[*].Name'
```

---

## 5. Database Setup

### 5.1 Run Migrations

```bash
cd apps/backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
alembic upgrade head
```

### 5.2 Seed Data

```bash
python scripts/seed_data.py
```

---

## 6. Docker Images

### 6.1 Build and Push (Manual)

```bash
# Get ECR login
aws ecr get-login-password --region eu-central-1 | \
  docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com

# Build and push all services
cd docker
docker build -t <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/pulse-ai-backend:latest -f backend.Dockerfile ../apps/backend
docker push <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/pulse-ai-backend:latest

docker build -t <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/pulse-ai-gateway:latest -f gateway.Dockerfile ../apps/gateway
docker push <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/pulse-ai-gateway:latest

docker build -t <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/pulse-ai-worker:latest -f worker.Dockerfile ../apps/worker
docker push <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/pulse-ai-worker:latest

docker build -t <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/pulse-ai-frontend:latest -f frontend.Dockerfile ../apps/frontend
docker push <ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/pulse-ai-frontend:latest
```

### 6.2 Or Use GitHub Actions

```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

GitHub Actions will automatically:
1. Build all 4 Docker images
2. Push to ECR
3. Update ECS services
4. Wait for stability

---

## 7. ECS Services Deployment

### 7.1 Update Task Definitions

```bash
cd scripts
./update_ecs_images.sh latest
```

### 7.2 Verify Services

```bash
aws ecs list-services --cluster pulse-ai-cluster
aws ecs describe-services --cluster pulse-ai-cluster --services pulse-ai-backend
```

---

## 8. DNS Configuration (Optional)

### 8.1 If Using Custom Domain

1. Go to Route53 console
2. Verify A/AAAA records point to CloudFront distribution
3. Wait for DNS propagation (5-60 minutes)

### 8.2 If Using Default Domains

Get ALB and CloudFront URLs from Terraform outputs:

```bash
terraform output
```

Access your app at:
- Frontend: `<cloudfront-domain>`
- API: `<alb-dns>/v1`
- Gateway: `<alb-dns>/gateway/v1`

---

## 9. Post-Deployment Testing

### 9.1 Health Checks

```bash
curl https://api.yourdomain.com/health
curl https://gateway.yourdomain.com/health
```

### 9.2 Test Magic Link Auth

1. Go to https://yourdomain.com
2. Enter email
3. Check SES sandbox (if using sandbox mode)
4. Click magic link
5. Should redirect to /app/chat

### 9.3 Test AI Chat

1. Login
2. Go to /app/chat
3. Select a model
4. Send a message
5. Verify response from AI

---

## 10. Monitoring

### 10.1 CloudWatch Dashboards

- Go to CloudWatch console
- Check "pulse-ai-*" dashboards
- Monitor: ECS CPU/Memory, RDS connections, ALB requests

### 10.2 Set Up Alarms

```bash
terraform apply -target=module.observability
```

This creates alarms for:
- ALB 5xx errors > 10
- ECS unhealthy tasks
- RDS CPU > 80%
- Redis CPU > 80%

---

## 11. Troubleshooting

### ECS Tasks Not Starting

```bash
aws ecs describe-tasks --cluster pulse-ai-cluster --tasks <task-arn>
# Check logs in CloudWatch: /ecs/pulse-ai-*
```

### Database Connection Issues

```bash
# Test from bastion or local with tunnel
psql -h <rds-endpoint> -U postgres -d pulse_ai
```

### API Keys Not Working

```bash
aws secretsmanager get-secret-value --secret-id OPENAI_API_KEY
```

---

## 12. Rolling Back

```bash
cd infra/terraform
terraform apply -target=module.ecs -var="image_tag=<previous-sha>"
```

Or revert git commit and push.

---

## 13. Scaling

### Horizontal Scaling (ECS)

Edit `infra/terraform/modules/ecs/main.tf`:

```hcl
desired_count = 3  # Increase from 1
```

Apply:

```bash
terraform apply -target=module.ecs
```

### Vertical Scaling (RDS)

Edit `infra/terraform/modules/rds/main.tf`:

```hcl
max_capacity = 8.0  # Increase from 4.0
```

---

## 14. Cost Optimization

**Expected Monthly Costs (us-east-1):**
- RDS Aurora Serverless v2: $50-150 (depends on usage)
- ElastiCache Redis: $15-30
- ECS Fargate: $60-120 (4 services)
- ALB: $20-30
- CloudFront: $5-20
- S3: $5-10
- **Total: ~$155-360/month**

**To Reduce Costs:**
1. Use spot instances for ECS (50% savings)
2. Reduce RDS max ACU to 2
3. Use smaller Redis node (cache.t3.micro)
4. Enable S3 lifecycle policies

---

## 15. Backup Strategy

### Automated Backups (Already Configured)

- RDS: Daily snapshots, 7-day retention
- S3: Versioning enabled on assets bucket

### Manual Backup

```bash
aws rds create-db-snapshot \
  --db-cluster-identifier pulse-ai-cluster \
  --db-cluster-snapshot-identifier pulse-ai-manual-$(date +%Y%m%d)
```

---

## 16. Security Checklist

- [ ] All secrets in Secrets Manager (no hardcoded)
- [ ] Security groups configured (least privilege)
- [ ] ALB uses HTTPS (if cert configured)
- [ ] RDS in private subnets
- [ ] S3 buckets not public
- [ ] CloudWatch logs enabled
- [ ] IAM roles follow least privilege
- [ ] MFA enabled on AWS account

---

## Support

For issues, check:
1. `docs/RUNBOOK.md` for operational procedures
2. CloudWatch logs: `/ecs/pulse-ai-*`
3. GitHub Issues: https://github.com/Samer-Is/pulse/issues

---

**Last Updated:** 2025-11-11

