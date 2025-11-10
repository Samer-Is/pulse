#!/bin/bash
# Update ECS services with new Docker images

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
CLUSTER_NAME=${ECS_CLUSTER:-"ai-studio-prod-cluster"}
REGION=${AWS_REGION:-"eu-central-1"}
IMAGE_TAG=${1:-"latest"}

if [ -z "$IMAGE_TAG" ]; then
    echo -e "${RED}❌ Error: Image tag required${NC}"
    echo "Usage: $0 <image-tag>"
    exit 1
fi

echo -e "${YELLOW}🚀 Updating ECS services with image tag: ${IMAGE_TAG}${NC}"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo ""

# Services to update
SERVICES=("frontend" "backend" "gateway" "worker")

update_service() {
    SERVICE_NAME="ai-studio-prod-$1"
    echo -e "${YELLOW}Updating $SERVICE_NAME...${NC}"
    
    # Get current task definition
    TASK_DEF=$(aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $REGION \
        --query 'services[0].taskDefinition' \
        --output text)
    
    echo "Current task definition: $TASK_DEF"
    
    # Get task definition JSON
    aws ecs describe-task-definition \
        --task-definition $TASK_DEF \
        --region $REGION \
        --query 'taskDefinition' \
        > task-def-$1.json
    
    # Extract ECR repository URL
    ECR_REPO=$(jq -r '.containerDefinitions[0].image | split(":")[0]' task-def-$1.json)
    NEW_IMAGE="$ECR_REPO:$IMAGE_TAG"
    
    echo "New image: $NEW_IMAGE"
    
    # Update image in task definition
    jq --arg IMAGE "$NEW_IMAGE" \
        'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy) | .containerDefinitions[0].image = $IMAGE' \
        task-def-$1.json > task-def-$1-updated.json
    
    # Register new task definition
    NEW_TASK_DEF=$(aws ecs register-task-definition \
        --cli-input-json file://task-def-$1-updated.json \
        --region $REGION \
        --query 'taskDefinition.taskDefinitionArn' \
        --output text)
    
    echo "Registered: $NEW_TASK_DEF"
    
    # Update service
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --task-definition $NEW_TASK_DEF \
        --force-new-deployment \
        --region $REGION \
        > /dev/null
    
    echo -e "${GREEN}✅ $SERVICE_NAME updated${NC}"
    
    # Cleanup
    rm task-def-$1.json task-def-$1-updated.json
    
    echo ""
}

# Update all services
for SERVICE in "${SERVICES[@]}"; do
    update_service $SERVICE
done

echo -e "${GREEN}=========================================="
echo "✅ All services updated!"
echo "==========================================${NC}"
echo ""
echo "Services are now deploying. Monitor progress:"
echo "  aws ecs describe-services --cluster $CLUSTER_NAME --services <service-name> --region $REGION"
echo ""
echo "Wait for stability:"
echo "  aws ecs wait services-stable --cluster $CLUSTER_NAME --services <service-name> --region $REGION"
echo ""

