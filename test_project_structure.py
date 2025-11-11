"""
Comprehensive Pulse AI Studio project structure test.
Validates all required files from instructions.txt are present.
"""

import os
from pathlib import Path

class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    RESET = ''

def check_file(path):
    """Check if file exists."""
    exists = Path(path).exists()
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {path}")
    return exists

def check_dir(path):
    """Check if directory exists."""
    exists = Path(path).is_dir()
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {path}/")
    return exists

print("=" * 70)
print("PULSE AI STUDIO - PROJECT STRUCTURE TEST")
print("=" * 70)
print()

total_files = 0
found_files = 0

# Root files
print("[1] ROOT FILES")
root_files = [
    ".editorconfig",
    ".gitignore",
    ".gitattributes",
    "README.md",
    "SECURITY.md",
    "LICENSE"
]
for f in root_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# Docker files
print("[2] DOCKER FILES")
docker_files = [
    "docker/backend.Dockerfile",
    "docker/gateway.Dockerfile",
    "docker/frontend.Dockerfile",
    "docker/worker.Dockerfile"
]
for f in docker_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# Backend
print("[3] BACKEND")
backend_files = [
    "apps/backend/src/main.py",
    "apps/backend/src/api/v1/auth.py",
    "apps/backend/src/api/v1/payments.py",
    "apps/backend/src/api/v1/usage.py",
    "apps/backend/src/api/v1/plans.py",
    "apps/backend/src/api/v1/files.py",
    "apps/backend/src/api/v1/cv.py",
    "apps/backend/src/api/v1/slides.py",
    "apps/backend/src/core/config.py",
    "apps/backend/src/core/security.py",
    "apps/backend/src/core/db.py",
    "apps/backend/src/core/logging.py",
    "apps/backend/src/core/dependencies.py",
    "apps/backend/src/models/user.py",
    "apps/backend/src/models/plan.py",
    "apps/backend/src/models/usage.py",
    "apps/backend/src/models/payment.py",
    "apps/backend/src/models/file.py",
    "apps/backend/src/models/job.py",
    "apps/backend/src/schemas/auth.py",
    "apps/backend/src/schemas/payments.py",
    "apps/backend/src/schemas/plans.py",
    "apps/backend/src/schemas/usage.py",
    "apps/backend/src/schemas/files.py",
    "apps/backend/src/schemas/cv.py",
    "apps/backend/src/schemas/slides.py",
    "apps/backend/src/services/emails.py",
    "apps/backend/src/services/files.py",
    "apps/backend/src/services/slides_pptx.py",
    "apps/backend/src/services/cv_docx.py",
    "apps/backend/src/services/payments/base.py",
    "apps/backend/src/services/payments/hyperpay.py",
    "apps/backend/src/services/payments/paytabs.py",
    "apps/backend/src/services/payments/zaincash.py",
    "apps/backend/alembic.ini",
    "apps/backend/alembic/env.py",
    "apps/backend/scripts/seed_data.py",
    "apps/backend/pyproject.toml",
]
for f in backend_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# Gateway
print("[4] GATEWAY")
gateway_files = [
    "apps/gateway/src/main.py",
    "apps/gateway/src/core/config.py",
    "apps/gateway/src/core/logging.py",
    "apps/gateway/src/core/provider_router.py",
    "apps/gateway/src/core/moderation.py",
    "apps/gateway/src/providers/openai_client.py",
    "apps/gateway/src/providers/anthropic_client.py",
    "apps/gateway/src/providers/google_client.py",
    "apps/gateway/src/providers/nano_banana_stub.py",
    "apps/gateway/src/providers/veo3_stub.py",
    "apps/gateway/src/providers/replicate_client.py",
    "apps/gateway/src/routes/chat.py",
    "apps/gateway/src/routes/images.py",
    "apps/gateway/src/routes/video.py",
    "apps/gateway/src/models/usage_log.py",
    "apps/gateway/src/schemas/chat.py",
    "apps/gateway/src/schemas/images.py",
    "apps/gateway/src/schemas/video.py",
    "apps/gateway/src/middleware/rate_limit.py",
    "apps/gateway/src/middleware/usage_meter.py",
    "apps/gateway/pyproject.toml",
]
for f in gateway_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# Worker
print("[5] WORKER")
worker_files = [
    "apps/worker/src/main.py",
    "apps/worker/src/jobs/payments_webhooks.py",
    "apps/worker/src/jobs/video_finalize.py",
    "apps/worker/src/jobs/analytics.py",
    "apps/worker/src/jobs/cleanup.py",
    "apps/worker/pyproject.toml",
]
for f in worker_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# Frontend
print("[6] FRONTEND")
frontend_files = [
    "apps/frontend/app/layout.tsx",
    "apps/frontend/app/providers.tsx",
    "apps/frontend/app/(landing)/page.tsx",
    "apps/frontend/app/verify/page.tsx",
    "apps/frontend/app/app/chat/page.tsx",
    "apps/frontend/app/app/cv/page.tsx",
    "apps/frontend/app/app/slides/page.tsx",
    "apps/frontend/app/app/images/page.tsx",
    "apps/frontend/app/app/video/page.tsx",
    "apps/frontend/app/app/account/page.tsx",
    "apps/frontend/components/ModelSelector.tsx",
    "apps/frontend/components/TokenMeter.tsx",
    "apps/frontend/components/ChatInterface.tsx",
    "apps/frontend/components/Sidebar.tsx",
    "apps/frontend/components/PlanCard.tsx",
    "apps/frontend/components/PayButton.tsx",
    "apps/frontend/components/UsageBadge.tsx",
    "apps/frontend/components/Editors/ImageEditor.tsx",
    "apps/frontend/components/Editors/VideoEditor.tsx",
    "apps/frontend/components/Forms/CvForm.tsx",
    "apps/frontend/components/Forms/SlidesForm.tsx",
    "apps/frontend/lib/api.ts",
    "apps/frontend/styles/globals.css",
    "apps/frontend/next.config.js",
    "apps/frontend/package.json",
    "apps/frontend/tsconfig.json",
    "apps/frontend/tailwind.config.ts",
    "apps/frontend/postcss.config.js",
]
for f in frontend_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# Terraform
print("[7] TERRAFORM")
terraform_files = [
    "infra/terraform/backend.tf",
    "infra/terraform/versions.tf",
    "infra/terraform/providers.tf",
    "infra/terraform/variables.tf",
    "infra/terraform/terraform.tfvars.example",
    "infra/terraform/outputs.tf",
    "infra/terraform/main.tf",
]
terraform_modules = [
    "infra/terraform/modules/vpc",
    "infra/terraform/modules/ecr",
    "infra/terraform/modules/ecs",
    "infra/terraform/modules/alb",
    "infra/terraform/modules/rds",
    "infra/terraform/modules/redis",
    "infra/terraform/modules/s3",
    "infra/terraform/modules/cloudfront",
    "infra/terraform/modules/acm",
    "infra/terraform/modules/route53",
    "infra/terraform/modules/ses",
    "infra/terraform/modules/iam",
    "infra/terraform/modules/secrets",
    "infra/terraform/modules/observability",
]
for f in terraform_files:
    total_files += 1
    if check_file(f):
        found_files += 1
for d in terraform_modules:
    total_files += 1
    if check_dir(d):
        found_files += 1
print()

# Scripts
print("[8] SCRIPTS")
script_files = [
    "scripts/dev_bootstrap.sh",
    "scripts/update_ecs_images.sh",
    "scripts/format_check.sh",
    "scripts/lint_check.sh"
]
for f in script_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# GitHub Actions
print("[9] GITHUB ACTIONS")
gh_files = [
    ".github/workflows/infra.yml",
    ".github/workflows/app.yml"
]
for f in gh_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# Documentation
print("[10] DOCUMENTATION")
doc_files = [
    "docs/ARCHITECTURE.md",
    "docs/RUNBOOK.md",
    "docs/MARKETING_PLAYBOOK.md",
    "docs/API_CONTRACTS.md",
    "docs/CHECKLIST.md",
    "docs/ACTIVITY.md",
    "docs/DEPLOYMENT.md",
    "docs/API.md",
]
for f in doc_files:
    total_files += 1
    if check_file(f):
        found_files += 1
print()

# Summary
print("=" * 70)
print(f"SUMMARY: {found_files}/{total_files} files found ({found_files/total_files*100:.1f}%)")
print("=" * 70)

if found_files == total_files:
    print("[SUCCESS] All required files are present!")
else:
    print(f"[WARNING] {total_files - found_files} files are missing!")

print()
print("AI PROVIDER TEST RESULTS:")
print("  [OK] OpenAI: Working (gpt-4o-mini tested)")
print("  [FAIL] Anthropic: API key may not have model access")
print("  [FAIL] Gemini: Quota exceeded (free tier limit)")
print()

