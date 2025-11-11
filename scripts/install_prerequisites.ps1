# Install Terraform and AWS CLI for Windows
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALLING TERRAFORM & AWS CLI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Install Chocolatey if not installed
Write-Host "[1/3] Checking Chocolatey..." -ForegroundColor Yellow
try {
    choco --version | Out-Null
    Write-Host "  [OK] Chocolatey is installed" -ForegroundColor Green
} catch {
    Write-Host "  [INSTALL] Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "  [OK] Chocolatey installed" -ForegroundColor Green
}

# Install Terraform
Write-Host ""
Write-Host "[2/3] Installing Terraform..." -ForegroundColor Yellow
choco install terraform -y
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Terraform installed" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Terraform installation failed" -ForegroundColor Red
    exit 1
}

# Install AWS CLI
Write-Host ""
Write-Host "[3/3] Installing AWS CLI..." -ForegroundColor Yellow
choco install awscli -y
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] AWS CLI installed" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] AWS CLI installation failed" -ForegroundColor Red
    exit 1
}

# Refresh environment
Write-Host ""
Write-Host "[REFRESH] Updating environment variables..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verify installations
Write-Host "Verifying installations..." -ForegroundColor Cyan
Write-Host ""

try {
    $tfVersion = terraform version
    Write-Host "[OK] Terraform: $tfVersion" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Terraform not in PATH yet. Restart PowerShell." -ForegroundColor Yellow
}

try {
    $awsVersion = aws --version
    Write-Host "[OK] AWS CLI: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] AWS CLI not in PATH yet. Restart PowerShell." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Close and restart PowerShell" -ForegroundColor White
Write-Host "2. Run: aws configure" -ForegroundColor White
Write-Host "3. Run: .\scripts\deploy_aws.ps1" -ForegroundColor White
Write-Host ""


