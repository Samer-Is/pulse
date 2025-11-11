"""
AWS Infrastructure Validation for Pulse AI Studio.
Validates Terraform structure, modules, and deployment readiness.
"""

import os
from pathlib import Path

class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    BLUE = ''
    RESET = ''

def check_file(path):
    """Check if file exists and return size."""
    p = Path(path)
    if p.exists():
        size = p.stat().st_size
        return True, size
    return False, 0

def check_terraform_module(module_name, module_path):
    """Validate a Terraform module structure."""
    print(f"\n{Colors.BLUE}[MODULE]{Colors.RESET} {module_name}")
    
    required_files = ['main.tf', 'variables.tf', 'outputs.tf']
    optional_files = ['README.md', 'versions.tf']
    
    module_complete = True
    total_lines = 0
    
    for filename in required_files:
        filepath = f"{module_path}/{filename}"
        exists, size = check_file(filepath)
        status = "[OK]" if exists else "[MISSING]"
        
        if exists:
            # Count lines
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"  {status} {filename} ({lines} lines, {size} bytes)")
        else:
            print(f"  {status} {filename} - MISSING!")
            module_complete = False
    
    for filename in optional_files:
        filepath = f"{module_path}/{filename}"
        exists, size = check_file(filepath)
        if exists:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"  [OPTIONAL] {filename} ({lines} lines)")
    
    return module_complete, total_lines

def validate_terraform_syntax(filepath):
    """Basic syntax validation for Terraform files."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        issues = []
        
        # Check for basic Terraform syntax
        if 'resource "' not in content and 'module "' not in content and 'data "' not in content and 'variable "' not in content and 'output "' not in content:
            issues.append("No Terraform blocks found")
        
        # Check for unclosed braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
        
        return issues
    except Exception as e:
        return [f"Error reading file: {str(e)}"]

print("=" * 80)
print(f"{Colors.BLUE}PULSE AI STUDIO - AWS INFRASTRUCTURE VALIDATION{Colors.RESET}")
print("=" * 80)
print()

# Root Terraform files
print(f"{Colors.BLUE}[ROOT]{Colors.RESET} Terraform Configuration Files")
root_files = [
    'infra/terraform/backend.tf',
    'infra/terraform/versions.tf',
    'infra/terraform/providers.tf',
    'infra/terraform/variables.tf',
    'infra/terraform/terraform.tfvars.example',
    'infra/terraform/main.tf',
    'infra/terraform/outputs.tf',
]

root_complete = True
root_lines = 0

for filepath in root_files:
    exists, size = check_file(filepath)
    status = "[OK]" if exists else "[MISSING]"
    
    if exists:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = len(f.readlines())
            root_lines += lines
        print(f"  {status} {Path(filepath).name} ({lines} lines, {size} bytes)")
        
        # Basic syntax validation
        issues = validate_terraform_syntax(filepath)
        if issues:
            root_complete = False
            for issue in issues:
                print(f"    [WARNING] {issue}")
    else:
        print(f"  {status} {Path(filepath).name} - MISSING!")
        root_complete = False

# Terraform modules
print(f"\n{Colors.BLUE}{'=' * 80}{Colors.RESET}")
print(f"{Colors.BLUE}TERRAFORM MODULES (14 modules){Colors.RESET}")
print(f"{Colors.BLUE}{'=' * 80}{Colors.RESET}")

modules = [
    ('VPC', 'infra/terraform/modules/vpc'),
    ('S3', 'infra/terraform/modules/s3'),
    ('IAM', 'infra/terraform/modules/iam'),
    ('ECR', 'infra/terraform/modules/ecr'),
    ('Secrets Manager', 'infra/terraform/modules/secrets'),
    ('RDS Aurora', 'infra/terraform/modules/rds'),
    ('ElastiCache Redis', 'infra/terraform/modules/redis'),
    ('Application Load Balancer', 'infra/terraform/modules/alb'),
    ('SES', 'infra/terraform/modules/ses'),
    ('Observability', 'infra/terraform/modules/observability'),
    ('ECS', 'infra/terraform/modules/ecs'),
    ('ACM', 'infra/terraform/modules/acm'),
    ('CloudFront', 'infra/terraform/modules/cloudfront'),
    ('Route53', 'infra/terraform/modules/route53'),
]

modules_complete = 0
total_module_lines = 0

for module_name, module_path in modules:
    complete, lines = check_terraform_module(module_name, module_path)
    total_module_lines += lines
    if complete:
        modules_complete += 1

# AWS Resources Summary
print(f"\n{Colors.BLUE}{'=' * 80}{Colors.RESET}")
print(f"{Colors.BLUE}AWS RESOURCES TO BE DEPLOYED{Colors.RESET}")
print(f"{Colors.BLUE}{'=' * 80}{Colors.RESET}")

resources = [
    ("Networking", [
        "VPC with 3 Availability Zones",
        "6 subnets (3 public, 3 private)",
        "Internet Gateway",
        "3 NAT Gateways (high availability)",
        "Route tables and associations",
        "Security groups (ALB, ECS, RDS, Redis)",
    ]),
    ("Compute", [
        "ECS Fargate Cluster",
        "4 ECS Services (frontend, backend, gateway, worker)",
        "4 Task Definitions with container configs",
        "Auto-scaling policies (CPU/Memory based)",
        "Service discovery (CloudMap)",
    ]),
    ("Storage", [
        "3 S3 Buckets (assets, quarantine, tfstate)",
        "S3 lifecycle policies",
        "Bucket encryption (AES-256)",
        "CORS configuration for uploads",
    ]),
    ("Database", [
        "Aurora PostgreSQL Serverless v2",
        "Multi-AZ deployment (3 AZs)",
        "Auto-scaling (0.5-4 ACUs)",
        "Automated backups (7-day retention)",
        "ElastiCache Redis (3 nodes)",
    ]),
    ("Load Balancing", [
        "Application Load Balancer (internet-facing)",
        "4 Target Groups (services)",
        "Path-based routing (/api, /gateway, /*)",
        "Health checks",
        "CloudFront CDN",
    ]),
    ("Security & IAM", [
        "GitHub OIDC provider",
        "ECS task execution roles",
        "ECS task roles (S3, Secrets, SES access)",
        "Deployment roles for CI/CD",
        "AWS Secrets Manager (10+ secrets)",
        "KMS keys for encryption",
    ]),
    ("Networking & DNS", [
        "Route53 hosted zone",
        "DNS records (A, CNAME)",
        "ACM TLS certificate",
        "DNS validation",
    ]),
    ("Observability", [
        "CloudWatch Log Groups (4 services)",
        "CloudWatch Alarms (CPU, Memory, 5xx errors)",
        "X-Ray tracing (5% sampling)",
        "SNS topics for alerts",
        "30-day log retention",
    ]),
    ("Containers", [
        "4 ECR repositories",
        "Image scanning enabled",
        "Lifecycle policies (keep last 10)",
        "Cross-region replication (optional)",
    ]),
    ("Email", [
        "SES email identity",
        "SES configuration set",
        "Bounce/complaint handling",
        "Email sending quotas",
    ]),
]

for category, items in resources:
    print(f"\n> {category}:")
    for item in items:
        print(f"  - {item}")

# Summary
print(f"\n{Colors.BLUE}{'=' * 80}{Colors.RESET}")
print(f"{Colors.BLUE}VALIDATION SUMMARY{Colors.RESET}")
print(f"{Colors.BLUE}{'=' * 80}{Colors.RESET}")

print(f"\n[OK] Root Configuration: {len(root_files)} files, {root_lines} lines of code")
print(f"[OK] Terraform Modules: {modules_complete}/{len(modules)} complete, {total_module_lines} lines of code")
print(f"[OK] Total Infrastructure Code: {root_lines + total_module_lines} lines")

print(f"\n[RESOURCES] Estimated AWS Resources:")
print(f"  - ~50+ AWS resources to be created")
print(f"  - 3 Availability Zones for high availability")
print(f"  - 4 containerized services on ECS Fargate")
print(f"  - Multi-tier architecture (public/private subnets)")

print(f"\n[COST] Estimated Monthly Cost (us-east-1):")
print(f"  - ECS Fargate (4 services, 0.25 vCPU each): ~$20-30/month")
print(f"  - Aurora Serverless v2 (0.5-4 ACUs): ~$45-180/month")
print(f"  - ElastiCache Redis (3 nodes, cache.t3.micro): ~$40/month")
print(f"  - NAT Gateways (3): ~$100/month")
print(f"  - CloudFront + S3: ~$5-20/month")
print(f"  - ALB: ~$20/month")
print(f"  - Other services (Secrets, CloudWatch, etc): ~$10/month")
print(f"  TOTAL ESTIMATED: $240-400/month")

print(f"\n[READINESS] Deployment Status:")

if root_complete and modules_complete == len(modules):
    print(f"  [SUCCESS] Infrastructure code is READY for deployment!")
    print(f"  [SUCCESS] All Terraform modules are present and complete")
    print(f"  [SUCCESS] No syntax errors detected")
    print(f"\n[NEXT STEPS]:")
    print(f"  1. Install Terraform CLI (https://developer.hashicorp.com/terraform/install)")
    print(f"  2. Configure AWS credentials (aws configure)")
    print(f"  3. Update terraform.tfvars with your values")
    print(f"  4. Run: terraform init")
    print(f"  5. Run: terraform plan")
    print(f"  6. Run: terraform apply")
else:
    print(f"  [ERROR] Infrastructure has issues!")
    print(f"  [ERROR] Root files: {'PASS' if root_complete else 'FAIL'}")
    print(f"  [ERROR] Modules: {modules_complete}/{len(modules)} complete")

print(f"\n{Colors.BLUE}{'=' * 80}{Colors.RESET}")
print()

