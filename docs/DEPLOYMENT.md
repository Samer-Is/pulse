# 🚀 Deployment Guide - Pulse AI Studio

This guide covers deploying Pulse AI Studio to AWS using Terraform and Docker.

## Table of Contents

- [Prerequisites](#prerequisites)
- [AWS Infrastructure Setup](#aws-infrastructure-setup)
- [Environment Configuration](#environment-configuration)
- [Docker Image Build & Push](#docker-image-build--push)
- [Application Deployment](#application-deployment)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **AWS CLI** 2.x configured with credentials
- **Terraform** 1.6+
- **Docker** 20.x+
- **Git** 2.x+
- **SSH** client

### Required Accounts & Keys

- AWS Account with programmatic access
- Stripe Account (test + live keys)
- OpenAI API Key
- Anthropic API Key
- Google Cloud Project with Vertex AI enabled
- Google OAuth 2.0 credentials

### AWS Credentials

```bash
# Configure AWS CLI
aws configure

AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: eu-central-1
Default output format: json

# Verify configuration
aws sts get-caller-identity
```

## AWS Infrastructure Setup

### 1. Initialize Terraform

```bash
cd infra/terraform/environments/dev

# Initialize Terraform providers
terraform init

# Validate configuration
terraform validate
```

### 2. Review Terraform Variables

Edit `terraform.tfvars` (create from `terraform.tfvars.example`):

```hcl
project_name        = "pulse"
aws_region          = "eu-central-1"
aws_account_id      = "YOUR_AWS_ACCOUNT_ID"
ec2_instance_type   = "t3.micro"
rds_instance_class  = "db.t4g.micro"
database_name       = "pulse"
database_username   = "pulse"
```

### 3. Deploy Infrastructure

```bash
# Preview changes
terraform plan

# Apply infrastructure changes
terraform apply

# Save outputs
terraform output > ../../outputs.txt
```

### Deployed Resources

After successful deployment:

```
✅ VPC with public subnets, Internet Gateway, Route Tables
✅ Security Groups (EC2, RDS)
✅ EC2 instance (t3.micro) with elastic IP
✅ RDS PostgreSQL instance (db.t4g.micro)
✅ S3 bucket for file exports
✅ SQS queue with Dead Letter Queue
✅ ECR repositories (pulse-api, pulse-web, pulse-workers)
✅ Secrets Manager secrets (pulse/api-keys, pulse/db-credentials)
✅ IAM roles and instance profiles
```

### 4. Note Important Outputs

```bash
# EC2 Public IP
terraform output ec2_public_ip

# RDS Endpoint
terraform output rds_endpoint

# S3 Bucket Name
terraform output s3_bucket_name

# SQS Queue URL
terraform output sqs_queue_url

# ECR Repository URLs
terraform output ecr_api_repository_url
terraform output ecr_web_repository_url
terraform output ecr_workers_repository_url
```

## Environment Configuration

### 1. Configure AWS Secrets Manager

Store sensitive credentials in AWS Secrets Manager:

```bash
# API Keys Secret
aws secretsmanager put-secret-value \
  --secret-id pulse/api-keys \
  --secret-string '{
    "OPENAI_API_KEY": "sk-...",
    "ANTHROPIC_API_KEY": "sk-ant-...",
    "GCP_VERTEX_PROJECT_ID": "your-project",
    "GCP_VERTEX_LOCATION": "us-central-1",
    "GCP_VERTEX_SA_JSON": "base64-encoded-json",
    "RUNWAY_API_KEY": "your-runway-key",
    "PIKA_API_KEY": "your-pika-key",
    "STRIPE_SECRET_KEY": "sk_live_...",
    "STRIPE_WEBHOOK_SECRET": "whsec_...",
    "GOOGLE_OAUTH_CLIENT_ID": "your-client-id",
    "GOOGLE_OAUTH_CLIENT_SECRET": "your-client-secret",
    "JWT_SECRET": "generate-strong-random-secret"
  }'

# Database Credentials Secret
aws secretsmanager put-secret-value \
  --secret-id pulse/db-credentials \
  --secret-string '{
    "username": "pulse",
    "password": "GENERATE_STRONG_PASSWORD"
  }'
```

### 2. Stripe Webhook Configuration

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-domain.com/api/v1/stripe/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook signing secret to Secrets Manager

### 3. Google OAuth Configuration

1. Google Cloud Console → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID
3. Authorized redirect URIs:
   - `https://your-domain.com/api/auth/callback/google`
   - `http://localhost:3000/api/auth/callback/google` (dev)
4. Copy client ID and secret to Secrets Manager

## Docker Image Build & Push

### 1. Authenticate with ECR

```bash
# Get ECR login command
aws ecr get-login-password --region eu-central-1 | \
  docker login --username AWS --password-stdin \
  YOUR_AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com
```

### 2. Build Docker Images

```bash
# From project root

# Build API image
docker build -t pulse-api:latest -f apps/api/Dockerfile .

# Build Web image
docker build -t pulse-web:latest -f apps/web/Dockerfile .

# Build Workers image
docker build -t pulse-workers:latest -f apps/workers/Dockerfile .
```

### 3. Tag Images

```bash
# Get ECR URLs from Terraform outputs
API_REPO=$(terraform -chdir=infra/terraform/environments/dev output -raw ecr_api_repository_url)
WEB_REPO=$(terraform -chdir=infra/terraform/environments/dev output -raw ecr_web_repository_url)
WORKERS_REPO=$(terraform -chdir=infra/terraform/environments/dev output -raw ecr_workers_repository_url)

# Tag images
docker tag pulse-api:latest $API_REPO:latest
docker tag pulse-web:latest $WEB_REPO:latest
docker tag pulse-workers:latest $WORKERS_REPO:latest

# Tag with version
VERSION=v0.1.0
docker tag pulse-api:latest $API_REPO:$VERSION
docker tag pulse-web:latest $WEB_REPO:$VERSION
docker tag pulse-workers:latest $WORKERS_REPO:$VERSION
```

### 4. Push Images to ECR

```bash
# Push latest tags
docker push $API_REPO:latest
docker push $WEB_REPO:latest
docker push $WORKERS_REPO:latest

# Push version tags
docker push $API_REPO:$VERSION
docker push $WEB_REPO:$VERSION
docker push $WORKERS_REPO:$VERSION
```

## Application Deployment

### 1. SSH to EC2 Instance

```bash
# Get EC2 public IP
EC2_IP=$(terraform -chdir=infra/terraform/environments/dev output -raw ec2_public_ip)

# SSH to EC2 (key pair created by Terraform)
ssh -i ~/.ssh/pulse-ec2-key.pem ec2-user@$EC2_IP
```

### 2. Install Docker on EC2

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
```

### 3. Create Production Docker Compose

On EC2 instance, create `/home/ec2-user/pulse/docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    image: YOUR_AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/pulse-api:latest
    container_name: pulse-api
    environment:
      ENVIRONMENT: production
      AWS_REGION: eu-central-1
      DATABASE_URL: postgresql://pulse:PASSWORD@RDS_ENDPOINT:5432/pulse
      S3_BUCKET_NAME: pulse-exports
      SQS_QUEUE_URL: SQS_QUEUE_URL
    ports:
      - "8000:8000"
    restart: unless-stopped

  web:
    image: YOUR_AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/pulse-web:latest
    container_name: pulse-web
    environment:
      NEXT_PUBLIC_API_BASE: https://your-domain.com
    ports:
      - "3000:3000"
    restart: unless-stopped
    depends_on:
      - api

  workers:
    image: YOUR_AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/pulse-workers:latest
    container_name: pulse-workers
    environment:
      AWS_REGION: eu-central-1
      SQS_QUEUE_URL: SQS_QUEUE_URL
      DATABASE_URL: postgresql://pulse:PASSWORD@RDS_ENDPOINT:5432/pulse
    restart: unless-stopped
    depends_on:
      - api
```

### 4. Pull and Run Containers

```bash
# Authenticate Docker with ECR
aws ecr get-login-password --region eu-central-1 | \
  docker login --username AWS --password-stdin \
  YOUR_AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com

# Pull images
docker-compose -f docker-compose.prod.yml pull

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Run Database Migrations

```bash
# Enter API container
docker exec -it pulse-api bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

## Post-Deployment

### 1. Configure DNS

Point your domain to EC2 public IP:

```
A record: your-domain.com → EC2_PUBLIC_IP
A record: api.your-domain.com → EC2_PUBLIC_IP
```

### 2. Set Up SSL/TLS (Optional but Recommended)

Install and configure Let's Encrypt with Certbot:

```bash
# Install Certbot
sudo yum install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal is configured automatically
sudo systemctl status certbot-renew.timer
```

### 3. Configure Nginx Reverse Proxy

Create `/etc/nginx/conf.d/pulse.conf`:

```nginx
upstream api {
    server localhost:8000;
}

upstream web {
    server localhost:3000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Health Checks

Verify services are running:

```bash
# Health endpoint
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/health/ready

# Frontend
curl http://localhost:3000
```

### 5. Monitor Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f api
docker-compose logs -f workers

# View last 100 lines
docker-compose logs --tail=100 api
```

## CI/CD with GitHub Actions

The repository includes GitHub Actions workflow for automated deployment.

### Setup

1. Add GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `AWS_ACCOUNT_ID`
   - `EC2_SSH_KEY` (private key)
   - `EC2_HOST` (EC2 public IP)

2. Push a git tag to trigger deployment:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The workflow will:
1. Build Docker images
2. Push to ECR
3. SSH to EC2
4. Pull new images
5. Restart containers

## Troubleshooting

### API Container Fails to Start

```bash
# Check logs
docker logs pulse-api

# Common issues:
# - Database connection failure → Check RDS security group
# - Secrets not loaded → Verify Secrets Manager permissions
# - Missing environment variables → Check docker-compose.prod.yml
```

### Database Connection Issues

```bash
# Test connection from EC2
telnet RDS_ENDPOINT 5432

# Check security group
aws ec2 describe-security-groups \
  --group-ids sg-xxx

# Ensure EC2 security group is allowed in RDS security group
```

### S3 Upload Failures

```bash
# Check IAM role permissions
aws iam get-role --role-name pulse-ec2-role

# Test S3 access from EC2
aws s3 ls s3://pulse-exports/
```

### SQS Queue Issues

```bash
# Check queue
aws sqs get-queue-attributes \
  --queue-url SQS_QUEUE_URL \
  --attribute-names All

# Check worker logs
docker logs pulse-workers
```

### SSL Certificate Issues

```bash
# Test renewal
sudo certbot renew --dry-run

# Check certificate
sudo certbot certificates
```

## Backup & Recovery

### Database Backups

```bash
# Manual backup
pg_dump -h RDS_ENDPOINT -U pulse -d pulse > backup.sql

# Restore
psql -h RDS_ENDPOINT -U pulse -d pulse < backup.sql
```

### S3 Backups

RDS automated backups are configured via Terraform. S3 lifecycle policies handle file retention.

## Monitoring & Alerts

### CloudWatch Logs

EC2 CloudWatch agent can be configured to ship Docker logs:

```bash
# Install CloudWatch agent
sudo yum install -y amazon-cloudwatch-agent

# Configure and start
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### Health Check Monitoring

Use AWS CloudWatch to monitor health endpoints:
- `/health/ready` - 200 OK expected
- `/health/live` - 200 OK expected

Set up alarms for:
- API response time > 2s
- Error rate > 5%
- EC2 CPU > 80%
- RDS connections > 80% of max

## Scaling Considerations

### Horizontal Scaling

1. Create Application Load Balancer
2. Create Auto Scaling Group with EC2 instances
3. Update security groups
4. Configure session affinity if needed

### Database Scaling

1. Upgrade RDS instance class
2. Enable read replicas
3. Configure connection pooling

### Worker Scaling

1. Increase SQS visibility timeout
2. Add more worker containers
3. Deploy workers on separate EC2 instances

## Cost Optimization

Current monthly costs (estimate):
- EC2 t3.micro: ~$7.50
- RDS db.t4g.micro: ~$12.50
- S3 + data transfer: ~$5
- SQS: Minimal (<$1)
- **Total**: ~$25-30/month

Tips to reduce costs:
- Use Reserved Instances for predictable workloads
- Enable S3 lifecycle policies
- Stop EC2 during off-hours (dev environments)
- Use spot instances for workers

---

For issues or questions, refer to the main README or open a GitHub issue.

