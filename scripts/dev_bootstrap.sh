#!/bin/bash
# Development environment bootstrap script

set -e

echo "🚀 Pulse AI Studio - Development Bootstrap"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisite() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
    echo "✅ $1 found"
}

echo -e "${YELLOW}Checking prerequisites...${NC}"
check_prerequisite "docker"
check_prerequisite "node"
check_prerequisite "python3"
check_prerequisite "terraform"

# Setup Backend
echo -e "\n${YELLOW}Setting up Backend...${NC}"
cd apps/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate || . venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env 2>/dev/null || true
echo -e "${GREEN}✅ Backend setup complete${NC}"
cd ../..

# Setup Gateway
echo -e "\n${YELLOW}Setting up Gateway...${NC}"
cd apps/gateway
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate || . venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env 2>/dev/null || true
echo -e "${GREEN}✅ Gateway setup complete${NC}"
cd ../..

# Setup Worker
echo -e "\n${YELLOW}Setting up Worker...${NC}"
cd apps/worker
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate || . venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env 2>/dev/null || true
echo -e "${GREEN}✅ Worker setup complete${NC}"
cd ../..

# Setup Frontend
echo -e "\n${YELLOW}Setting up Frontend...${NC}"
cd apps/frontend
npm install
cp .env.example .env.local 2>/dev/null || true
echo -e "${GREEN}✅ Frontend setup complete${NC}"
cd ../..

# Setup Terraform
echo -e "\n${YELLOW}Setting up Terraform...${NC}"
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars 2>/dev/null || true
echo -e "${GREEN}✅ Terraform setup complete${NC}"
cd ../..

# Create local Docker network
echo -e "\n${YELLOW}Creating Docker network...${NC}"
docker network create ai-studio-network 2>/dev/null || echo "Network already exists"
echo -e "${GREEN}✅ Docker network ready${NC}"

echo -e "\n${GREEN}=========================================="
echo "✅ Bootstrap complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env files in apps/* with your configuration"
echo "2. Update infra/terraform/terraform.tfvars with your AWS details"
echo "3. Run services locally:"
echo "   - Backend: cd apps/backend && uvicorn src.main:app --reload --port 8080"
echo "   - Gateway: cd apps/gateway && uvicorn src.main:app --reload --port 8081"
echo "   - Frontend: cd apps/frontend && npm run dev"
echo "4. Or use Docker Compose (if configured)"
echo ""
echo "For deployment:"
echo "   cd infra/terraform && terraform init && terraform apply"
echo ""
