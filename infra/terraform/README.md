# Pulse AI Studio - Terraform Infrastructure

Infrastructure as Code for deploying Pulse AI Studio to AWS using Terraform.

## Architecture

- **VPC:** 3 AZs, public + private subnets, NAT Gateways
- **ECS Fargate:** 4 services (frontend, backend, gateway, worker)
- **ALB:** Application Load Balancer with path-based routing
- **Aurora PostgreSQL Serverless v2:** Database
- **ElastiCache Redis:** Caching and rate limiting
- **S3:** Assets, quarantine, Terraform state
- **CloudFront:** CDN (optional, with custom domain)
- **SES:** Email sending
- **Secrets Manager:** All API keys and credentials
- **CloudWatch + X-Ray:** Observability

## Prerequisites

- AWS CLI configured
- Terraform 1.5+
- AWS account with appropriate permissions

## Initial Setup

### 1. Configure Variables

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS account ID, region, etc.
```

### 2. Bootstrap State Backend

On first run, Terraform will create the S3 bucket and DynamoDB table for remote state:

```bash
terraform init
```

### 3. Plan and Apply

```bash
# Review changes
terraform plan

# Apply infrastructure
terraform apply
```

**Note:** First apply will take ~15-20 minutes to provision all resources.

## Modules

Each module is self-contained and can be used independently:

| Module | Purpose | Status |
|--------|---------|--------|
| `vpc` | VPC, subnets, NAT gateways | ⚠️ To be implemented |
| `ecr` | ECR repositories | ⚠️ To be implemented |
| `ecs` | ECS cluster, services, task definitions | ⚠️ To be implemented |
| `alb` | Application Load Balancer, target groups | ⚠️ To be implemented |
| `rds` | Aurora PostgreSQL Serverless v2 | ⚠️ To be implemented |
| `redis` | ElastiCache Redis | ⚠️ To be implemented |
| `s3` | S3 buckets (assets, quarantine, tfstate) | ⚠️ To be implemented |
| `cloudfront` | CloudFront distribution | ⚠️ To be implemented |
| `acm` | ACM certificates | ⚠️ To be implemented |
| `route53` | DNS records | ⚠️ To be implemented |
| `ses` | SES configuration | ⚠️ To be implemented |
| `iam` | IAM roles (ECS tasks, GitHub OIDC) | ⚠️ To be implemented |
| `secrets` | Secrets Manager placeholders | ⚠️ To be implemented |
| `observability` | CloudWatch, X-Ray, alarms | ⚠️ To be implemented |

**Status Key:**
- ✅ Implemented
- ⚠️ To be implemented (structure ready)
- ❌ Blocked/Issues

## GitHub Actions OIDC

The IAM module creates two OIDC roles for GitHub Actions:

1. **gha-infra-role** - For running Terraform (plan/apply)
2. **gha-deploy-role** - For deploying applications (ECR push, ECS update)

No long-lived AWS access keys required!

## Secrets Management

All secrets are stored in AWS Secrets Manager. After first apply, populate secrets:

```bash
# OpenAI API Key
aws secretsmanager put-secret-value \
  --secret-id OPENAI_API_KEY \
  --secret-string "sk-..."

# Database URL (automatically created by RDS module)
# JWT Secret
aws secretsmanager put-secret-value \
  --secret-id AI_STUDIO_JWT_SECRET \
  --secret-string "$(openssl rand -hex 32)"

# ... repeat for all required secrets
```

See `modules/secrets/README.md` for full list.

## Custom Domain Setup

To use a custom domain:

1. Set `domain_name` and `hosted_zone_id` in `terraform.tfvars`
2. Run `terraform apply`
3. Terraform will:
   - Create ACM certificates
   - Configure CloudFront
   - Add Route53 DNS records

## Outputs

After apply, important outputs are displayed:

```bash
terraform output
```

Key outputs:
- `alb_dns_name` - ALB domain (if not using custom domain)
- `ecr_repositories` - ECR repository URLs for Docker images
- `github_oidc_role_arn_infra` - Role ARN for GitHub Actions (infra)
- `github_oidc_role_arn_deploy` - Role ARN for GitHub Actions (deploy)

## Troubleshooting

### State Bucket Not Found

On first run, state bucket doesn't exist yet. This is normal. Terraform will create it automatically.

### Certificate Validation Timeout

ACM certificate validation can take 5-30 minutes. If timeout, re-run `terraform apply`.

### ECS Tasks Not Starting

Check:
1. ECR images exist (run app deployment first)
2. Secrets Manager has all required secrets
3. ECS task logs in CloudWatch

## Destroying Infrastructure

**WARNING:** This will delete all resources and data!

```bash
# Empty S3 buckets first (Terraform can't delete non-empty buckets)
aws s3 rm s3://ai-studio-assets --recursive
aws s3 rm s3://ai-studio-quarantine --recursive

# Destroy
terraform destroy
```

## CI/CD Integration

This infrastructure is designed to be deployed via GitHub Actions. See `/.github/workflows/infra.yml`.

Manual apply is for initial bootstrap only.

## Cost Estimation

Estimated monthly cost (eu-central-1, moderate usage):

- ECS Fargate (4 services, 24/7): ~$150-200
- Aurora Serverless v2 (0.5-4 ACU): ~$50-150
- ElastiCache Redis (t4g.micro): ~$15
- ALB: ~$20
- NAT Gateways (3 AZ): ~$100
- S3 + CloudFront: ~$20-50
- **Total: ~$350-550/month**

Scale down for development:
- Reduce task counts
- Lower ACU limits
- Use 1 AZ instead of 3

## Module Implementation Guide

Each module should follow this structure:

```
modules/<module-name>/
├── main.tf         # Resources
├── variables.tf    # Input variables
├── outputs.tf      # Output values
└── README.md       # Module documentation
```

See `/docs/ARCHITECTURE.md` for detailed architecture diagrams.

## Support

For issues:
1. Check CloudWatch logs
2. Review ACTIVITY.md for deployment history
3. Open GitHub issue with trace_id

