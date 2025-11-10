#!/bin/bash
# Code formatting check script

set -e

echo "🔍 Running code formatting checks..."

# Python (Black)
echo "Checking Python formatting (Black)..."
black --check apps/backend/src apps/gateway/src apps/worker/src || {
    echo "❌ Python formatting issues found. Run: black apps/backend/src apps/gateway/src apps/worker/src"
    exit 1
}
echo "✅ Python formatting OK"

# Python (isort)
echo "Checking Python imports (isort)..."
isort --check-only apps/backend/src apps/gateway/src apps/worker/src || {
    echo "❌ Python import sorting issues found. Run: isort apps/backend/src apps/gateway/src apps/worker/src"
    exit 1
}
echo "✅ Python imports OK"

# TypeScript/JavaScript (Prettier)
echo "Checking TypeScript/JavaScript formatting (Prettier)..."
cd apps/frontend
npm run format:check || {
    echo "❌ TypeScript formatting issues found. Run: npm run format"
    exit 1
}
cd ../..
echo "✅ TypeScript formatting OK"

# Terraform
echo "Checking Terraform formatting..."
terraform fmt -check -recursive infra/terraform/ || {
    echo "❌ Terraform formatting issues found. Run: terraform fmt -recursive infra/terraform/"
    exit 1
}
echo "✅ Terraform formatting OK"

echo ""
echo "✅ All formatting checks passed!"
