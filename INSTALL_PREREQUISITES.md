# Install Prerequisites for Deployment

## Required Tools:
1. ✅ **Terraform** - Already installed (C:\terraform\terraform.exe)
2. ❌ **Docker Desktop** - Not installed
3. ❌ **AWS CLI** - Not installed

---

## Step 1: Install Docker Desktop for Windows

### Download:
https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

### Installation Steps:
1. Download the installer from the link above
2. Run `Docker Desktop Installer.exe`
3. Follow the installation wizard
4. **Enable WSL 2** when prompted (recommended)
5. Restart your computer if required
6. Launch Docker Desktop
7. Wait for Docker to start (whale icon in system tray should be green)

### Verify Installation:
```powershell
docker --version
docker run hello-world
```

**Expected Output**: `Docker version 24.x.x` or similar

---

## Step 2: Install AWS CLI v2

### Download:
https://awscli.amazonaws.com/AWSCLIV2.msi

### Installation Steps:
1. Download the MSI installer
2. Run the installer
3. Follow the installation wizard (keep default settings)
4. Open a **NEW** PowerShell window

### Verify Installation:
```powershell
aws --version
```

**Expected Output**: `aws-cli/2.x.x Python/3.x.x Windows/10`

---

## Step 3: Verify AWS Credentials

Your AWS credentials should already be configured at:
```
C:\Users\s.ismail\.aws\credentials
C:\Users\s.ismail\.aws\config
```

Verify they work:
```powershell
aws sts get-caller-identity --region us-east-1
```

**Expected Output**:
```json
{
    "UserId": "...",
    "Account": "669633199086",
    "Arn": "arn:aws:iam::669633199086:user/..."
}
```

---

## Quick Install Script (Run as Administrator)

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Docker Desktop
choco install docker-desktop -y

# Install AWS CLI
choco install awscli -y

# Refresh environment
refreshenv
```

**Note**: After installation, you MUST restart PowerShell and Docker Desktop.

---

## After Installation:

Once both tools are installed, return here and run:

```powershell
cd C:\Users\s.ismail\Desktop\AI_STUDIO
# Then proceed with deployment
```

---

## Time Estimates:

- Docker Desktop download: ~5 minutes (600 MB)
- Docker Desktop installation: ~5 minutes
- AWS CLI download: ~1 minute (35 MB)
- AWS CLI installation: ~2 minutes
- **Total**: ~15-20 minutes

---

## Troubleshooting:

### Docker Desktop won't start?
- Enable virtualization in BIOS
- Enable WSL 2: `wsl --install`
- Restart computer

### AWS CLI not recognized?
- Close and reopen PowerShell
- Check PATH: `$env:PATH`

### Docker permission denied?
- Add your user to "docker-users" group
- Restart Docker Desktop

---

## Next Steps After Installation:

1. ✅ Verify Docker: `docker --version`
2. ✅ Verify AWS CLI: `aws --version`
3. ✅ Test Docker: `docker run hello-world`
4. ✅ Test AWS: `aws sts get-caller-identity`
5. 🚀 Proceed with deployment!

---

## Alternative: Use GitHub Actions

If you prefer not to install Docker locally, you can:
1. Push your code to GitHub
2. GitHub Actions will build and deploy automatically
3. See `.github/workflows/app.yml` for the workflow

---

Ready? Once installed, let me know and we'll proceed with the deployment!

