#!/bin/bash
# Linting check script

set -e

echo "🔍 Running linting checks..."

# Python (Ruff)
echo "Linting Python code (Ruff)..."
ruff check apps/backend/src apps/gateway/src apps/worker/src || {
    echo "❌ Python linting issues found"
    exit 1
}
echo "✅ Python linting OK"

# Python (MyPy)
echo "Type checking Python code (MyPy)..."
mypy apps/backend/src || {
    echo "⚠️  Python type checking issues found (non-blocking)"
}

# TypeScript (ESLint)
echo "Linting TypeScript code (ESLint)..."
cd apps/frontend
npm run lint || {
    echo "❌ TypeScript linting issues found"
    exit 1
}
cd ../..
echo "✅ TypeScript linting OK"

# TypeScript (Type check)
echo "Type checking TypeScript code..."
cd apps/frontend
npm run type-check || {
    echo "❌ TypeScript type checking failed"
    exit 1
}
cd ../..
echo "✅ TypeScript type checking OK"

echo ""
echo "✅ All linting checks passed!"
