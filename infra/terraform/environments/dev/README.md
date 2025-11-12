# Pulse AI Studio - Dev Environment

This directory contains Terraform configuration for the development environment.

## Prerequisites

- Terraform >= 1.6
- AWS CLI configured with valid credentials
- Access to AWS account with appropriate permissions

## Quick Start

### 1. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

Review the plan and type `yes` to proceed.

### 5. View Outputs

```bash
terraform output
terraform output -json > outputs.json
```

## What Gets Created

- **VPC**: Custom VPC with 2 public subnets
- **EC2**: t3.micro instance with Docker installed
- **RDS**: db.t4g.micro PostgreSQL 16
- **S3**: Bucket for exports
- **SQS**: Queue for async jobs + DLQ
- **ECR**: 3 repositories (web, api, workers)
- **Secrets Manager**: Placeholders for all secrets
- **IAM**: Roles and policies for EC2

## Cost Estimate

Monthly cost (approximate):
- EC2 t3.micro: ~$7.50
- RDS db.t4g.micro: ~$12.00
- S3 (minimal usage): ~$1.00
- Other services: ~$5.00
- **Total: ~$25-30/month**

## Post-Deployment Steps

1. **Update Secrets**: Add API keys to AWS Secrets Manager
2. **SSH Access**: Connect to EC2 and setup application
3. **Deploy Code**: Push Docker images to ECR
4. **Run Application**: Start services with Docker Compose

## Managing Infrastructure

### View Resources

```bash
terraform show
terraform state list
```

### Update Infrastructure

```bash
# After changing *.tf files
terraform plan
terraform apply
```

### Destroy Infrastructure

```bash
terraform destroy
```

⚠️ **Warning**: This will delete all resources including databases!

## Troubleshooting

### State Lock Issues

```bash
terraform force-unlock <lock-id>
```

### Refresh State

```bash
terraform refresh
```

### Import Existing Resources

```bash
terraform import <resource_type>.<name> <resource_id>
```

## Security Notes

- Never commit `terraform.tfvars` or `*.tfstate` files
- Restrict SSH access (`ssh_allowed_ips`) to your IP only
- Rotate AWS credentials regularly
- Use IAM roles instead of access keys where possible

