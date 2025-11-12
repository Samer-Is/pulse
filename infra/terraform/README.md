# Pulse AI Studio - Terraform Infrastructure

Infrastructure as Code for AWS deployment.

## Structure

```
terraform/
├── modules/          # Reusable Terraform modules
│   ├── vpc/         # VPC, subnets, security groups
│   ├── ec2/         # EC2 instances
│   ├── rds/         # RDS Postgres
│   ├── s3/          # S3 buckets
│   ├── sqs/         # SQS queues
│   ├── ecr/         # ECR repositories
│   └── secrets/     # Secrets Manager
└── environments/     # Environment-specific configs
    ├── dev/         # Development environment
    └── prod/        # Production environment
```

## Usage

### Prerequisites

- Terraform >= 1.6
- AWS CLI configured
- AWS credentials with appropriate permissions

### Deploy Development Environment

```bash
cd environments/dev
terraform init
terraform plan
terraform apply
```

### Outputs

After applying, Terraform will output:
- EC2 public DNS
- RDS endpoint
- S3 bucket name
- SQS queue URL
- ECR repository URLs

## Cost Optimization

- Using t3.micro/t4g.micro instances
- Minimal always-on resources
- Targeted for ~$50/month AWS spend

