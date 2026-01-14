#!/bin/bash
set -e

NAMESPACE="stockster"
REGISTRY="ghcr.io/${GITHUB_USER:-onelock}"

# Get current image versions
echo "Current deployment versions:"
kubectl get deployment stockster-dashboard -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}'
echo ""
kubectl get cronjob stockster-scraper -n $NAMESPACE -o jsonpath='{.spec.jobTemplate.spec.template.spec.containers[0].image}'
echo -e "\n"

# List available image tags from GitHub Container Registry
echo "Available versions in registry:"
echo "Dashboard tags:"
echo "  $(docker images --format '{{.Tag}}' $REGISTRY/stockster-dashboard | grep -v latest | head -5)"
echo "Scraper tags:"
echo "  $(docker images --format '{{.Tag}}' $REGISTRY/stockster-scraper | grep -v latest | head -5)"
echo ""

# Ask for version to deploy
read -p "Enter image tag to deploy (or 'latest'): " IMAGE_TAG

if [ -z "$IMAGE_TAG" ]; then
    echo "Error: No image tag provided"
    exit 1
fi

echo "Deploying version: $IMAGE_TAG"

# Update dashboard deployment
echo "Updating dashboard deployment..."
kubectl set image deployment/stockster-dashboard \
    dashboard=$REGISTRY/stockster-dashboard:$IMAGE_TAG \
    -n $NAMESPACE

# Update scraper cronjob
echo "Updating scraper cronjob..."
kubectl set image cronjob/stockster-scraper \
    scraper=$REGISTRY/stockster-scraper:$IMAGE_TAG \
    -n $NAMESPACE

echo ""
echo "✓ Deployment updated to version: $IMAGE_TAG"
echo ""
echo "Monitor rollout status:"
echo "  kubectl rollout status deployment/stockster-dashboard -n $NAMESPACE"
echo ""
echo "To rollback if needed:"
echo "  kubectl rollout undo deployment/stockster-dashboard -n $NAMESPACE"
