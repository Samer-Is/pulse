# 🚀 DEPLOY PULSE AI STUDIO TO AWS - RIGHT NOW

## Prerequisites You Need:

### 1. Install Terraform CLI
**Windows (PowerShell as Administrator):**
```powershell
# Using Chocolatey
choco install terraform

# OR download manually from:
# https://developer.hashicorp.com/terraform/install
```

**Verify installation:**
```bash
terraform version
```

### 2. Install AWS CLI
**Windows:**
```powershell
# Download and install from:
# https://awscli.amazonaws.com/AWSCLIV2.msi

# OR using Chocolatey:
choco install awscli
```

**Verify installation:**
```bash
aws --version
```

### 3. Configure AWS Credentials

You need an AWS account with admin access. Then run:

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: [Your AWS access key]
- **AWS Secret Access Key**: [Your AWS secret key]
- **Default region**: us-east-1
- **Default output format**: json

---

## 🔥 DEPLOY IN 6 COMMANDS:

Once you have Terraform and AWS CLI installed:

```bash
# 1. Navigate to Terraform directory
cd infra/terraform

# 2. Copy example tfvars
cp terraform.tfvars.example terraform.tfvars

# 3. Edit terraform.tfvars with your values
notepad terraform.tfvars
```

**EDIT THESE VALUES in terraform.tfvars:**
```hcl
# Required - Replace with your values
project_name = "pulse-ai-studio"
environment  = "prod"
aws_region   = "us-east-1"

# Domain settings - REQUIRED
domain_name = "yourdomain.com"              # ← YOUR DOMAIN
ses_from_email = "noreply@yourdomain.com"    # ← YOUR EMAIL

# GitHub repo for OIDC
github_repo = "Samer-Is/pulse"               # Already set!

# Database settings
db_name = "pulse_ai_db"
db_master_username = "pulse_admin"
# db_master_password will be auto-generated

# ECS settings (keep defaults or adjust)
backend_cpu    = 256
backend_memory = 512
gateway_cpu    = 256
gateway_memory = 512
frontend_cpu   = 256
frontend_memory = 512
worker_cpu     = 256
worker_memory  = 512

# Scaling settings
backend_min_tasks = 1
backend_max_tasks = 4
gateway_min_tasks = 1
gateway_max_tasks = 4
```

**Then deploy:**

```bash
# 4. Initialize Terraform (downloads providers)
terraform init

# 5. Preview what will be created (~50 resources)
terraform plan

# 6. DEPLOY TO AWS! (takes 20-30 minutes)
terraform apply
# Type "yes" when prompted
```

---

## ⏱️ What Happens During Deployment:

**Minute 0-5:** Creating VPC, subnets, NAT gateways, security groups  
**Minute 5-8:** Creating S3 buckets, IAM roles, ECR repositories  
**Minute 8-18:** Launching Aurora PostgreSQL + Redis (slowest part)  
**Minute 18-23:** Creating ALB, CloudFront, Route53, ACM  
**Minute 23-30:** Deploying ECS cluster and services  

**Total: ~25-30 minutes**

---

## 🎯 After Deployment:

1. **Get outputs:**
```bash
terraform output -json > outputs.json
```

2. **Update GitHub Secrets** (for CI/CD):
   - Go to https://github.com/Samer-Is/pulse/settings/secrets/actions
   - Add these secrets from `outputs.json`:
     - `AWS_ACCOUNT_ID`
     - `ECR_REGISTRY`
     - `ECS_CLUSTER_NAME`

3. **Build and push Docker images:**
```bash
# Trigger GitHub Actions by pushing to main
git push origin master
```

4. **Seed database:**
```bash
# SSH into backend ECS task and run:
alembic upgrade head
python scripts/seed_data.py
```

5. **Access your app:**
   - Frontend: `https://yourdomain.com`
   - Backend API: `https://yourdomain.com/api`
   - Gateway: `https://yourdomain.com/gateway`

---

## 💰 Cost Reminder:

Running this infrastructure will cost approximately:
- **$8-13/day** (~$240-400/month)
- Charges begin as soon as `terraform apply` completes

**To avoid charges, destroy when done testing:**
```bash
terraform destroy
```

---

## 🚨 Troubleshooting:

### "Error: AWS credentials not found"
→ Run `aws configure` first

### "Error: domain name not provided"
→ Edit `terraform.tfvars` and set your domain

### "Error: AWS quotas exceeded"
→ Request quota increases in AWS Service Quotas console

### Deployment stuck on RDS/Redis
→ This is normal, databases take 10-15 minutes

---

## ⚡ QUICK START (Copy-Paste):

```bash
# Install prerequisites
choco install terraform awscli

# Configure AWS
aws configure

# Deploy
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars  # Edit your domain and email
terraform init
terraform plan
terraform apply  # Type "yes"
```

**Then wait 25-30 minutes and your infrastructure is live!**

