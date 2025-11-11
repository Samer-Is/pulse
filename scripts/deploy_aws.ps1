# PowerShell deployment script for Windows
# Deploys Pulse AI Studio infrastructure to AWS

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PULSE AI STUDIO - AWS DEPLOYMENT SCRIPT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[1/7] Checking prerequisites..." -ForegroundColor Yellow

# Check Terraform
try {
    $tfVersion = terraform version
    Write-Host "  [OK] Terraform installed: $tfVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Terraform not found!" -ForegroundColor Red
    Write-Host "  Install with: choco install terraform" -ForegroundColor Red
    Write-Host "  Or download from: https://developer.hashicorp.com/terraform/install" -ForegroundColor Red
    exit 1
}

# Check AWS CLI
try {
    $awsVersion = aws --version
    Write-Host "  [OK] AWS CLI installed: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] AWS CLI not found!" -ForegroundColor Red
    Write-Host "  Install with: choco install awscli" -ForegroundColor Red
    Write-Host "  Or download from: https://awscli.amazonaws.com/AWSCLIV2.msi" -ForegroundColor Red
    exit 1
}

# Check AWS credentials
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "  [OK] AWS credentials configured" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] AWS credentials not configured!" -ForegroundColor Red
    Write-Host "  Run: aws configure" -ForegroundColor Red
    exit 1
}

# Navigate to Terraform directory
Write-Host ""
Write-Host "[2/7] Navigating to Terraform directory..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\infra\terraform"
Write-Host "  [OK] Current directory: $(Get-Location)" -ForegroundColor Green

# Check if terraform.tfvars exists
Write-Host ""
Write-Host "[3/7] Checking terraform.tfvars..." -ForegroundColor Yellow
if (-Not (Test-Path "terraform.tfvars")) {
    Write-Host "  [WARNING] terraform.tfvars not found!" -ForegroundColor Yellow
    Write-Host "  Creating from example..." -ForegroundColor Yellow
    Copy-Item "terraform.tfvars.example" "terraform.tfvars"
    Write-Host "  [IMPORTANT] Please edit terraform.tfvars with your values!" -ForegroundColor Red
    Write-Host "  Required: domain_name, ses_from_email" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Opening terraform.tfvars for editing..." -ForegroundColor Yellow
    Start-Process notepad "terraform.tfvars"
    Write-Host ""
    $continue = Read-Host "Have you edited terraform.tfvars? (yes/no)"
    if ($continue -ne "yes") {
        Write-Host "  [ABORT] Please edit terraform.tfvars and run this script again." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  [OK] terraform.tfvars exists" -ForegroundColor Green
}

# Initialize Terraform
Write-Host ""
Write-Host "[4/7] Initializing Terraform..." -ForegroundColor Yellow
terraform init
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Terraform init failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Terraform initialized" -ForegroundColor Green

# Validate Terraform configuration
Write-Host ""
Write-Host "[5/7] Validating Terraform configuration..." -ForegroundColor Yellow
terraform validate
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Terraform validation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Configuration is valid" -ForegroundColor Green

# Run Terraform plan
Write-Host ""
Write-Host "[6/7] Running Terraform plan..." -ForegroundColor Yellow
Write-Host "  This shows what resources will be created..." -ForegroundColor Cyan
Write-Host ""
terraform plan -out=tfplan
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Terraform plan failed!" -ForegroundColor Red
    exit 1
}

# Ask for confirmation
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "READY TO DEPLOY!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will create approximately 50 AWS resources:" -ForegroundColor Yellow
Write-Host "  - VPC with 3 Availability Zones" -ForegroundColor White
Write-Host "  - ECS Fargate cluster (4 services)" -ForegroundColor White
Write-Host "  - Aurora PostgreSQL Serverless v2" -ForegroundColor White
Write-Host "  - ElastiCache Redis" -ForegroundColor White
Write-Host "  - Application Load Balancer" -ForegroundColor White
Write-Host "  - CloudFront CDN" -ForegroundColor White
Write-Host "  - S3 buckets, IAM roles, and more..." -ForegroundColor White
Write-Host ""
Write-Host "Estimated monthly cost: `$240-400/month" -ForegroundColor Red
Write-Host "Deployment time: 25-30 minutes" -ForegroundColor Yellow
Write-Host ""

$deploy = Read-Host "Do you want to proceed with deployment? (yes/no)"
if ($deploy -ne "yes") {
    Write-Host "  [ABORT] Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

# Deploy!
Write-Host ""
Write-Host "[7/7] Deploying to AWS..." -ForegroundColor Yellow
Write-Host "  This will take 25-30 minutes. Please wait..." -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
terraform apply tfplan
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Terraform apply failed!" -ForegroundColor Red
    exit 1
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Duration: $($duration.Minutes) minutes $($duration.Seconds) seconds" -ForegroundColor Cyan
Write-Host ""

# Save outputs
Write-Host "Saving outputs to outputs.json..." -ForegroundColor Yellow
terraform output -json | Out-File -FilePath "outputs.json"
Write-Host "  [OK] Outputs saved to outputs.json" -ForegroundColor Green

Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Review outputs.json for resource details" -ForegroundColor White
Write-Host "  2. Update GitHub Secrets with AWS credentials" -ForegroundColor White
Write-Host "  3. Push to GitHub to trigger Docker builds" -ForegroundColor White
Write-Host "  4. Run database migrations and seed data" -ForegroundColor White
Write-Host ""
Write-Host "To destroy infrastructure: terraform destroy" -ForegroundColor Yellow
Write-Host ""


