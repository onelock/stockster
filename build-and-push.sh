#!/bin/bash
set -e

# GitHub username (change this to your GitHub username)
GITHUB_USER="${GITHUB_USER:-onelock}"
REGISTRY="ghcr.io/${GITHUB_USER,,}"  # Convert to lowercase

# Generate unique image tag
# Use git commit SHA if available, otherwise use timestamp
if git rev-parse --git-dir > /dev/null 2>&1; then
    GIT_SHA=$(git rev-parse --short HEAD)
    GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    IMAGE_TAG="${GIT_SHA}"
    echo "Using git commit SHA: $IMAGE_TAG (branch: $GIT_BRANCH)"
else
    IMAGE_TAG=$(date +%Y%m%d-%H%M%S)
    echo "Git not available, using timestamp: $IMAGE_TAG"
fi

echo "Building images with tag: $IMAGE_TAG"

# Build images
docker build -f Dockerfile.scraper -t stockster-scraper:$IMAGE_TAG .
docker build -f Dockerfile.dashboard -t stockster-dashboard:$IMAGE_TAG .
docker build -f Dockerfile.api -t stockster-api:$IMAGE_TAG .

echo "Tagging images for GitHub Container Registry..."

# Tag with unique identifier
docker tag stockster-scraper:$IMAGE_TAG $REGISTRY/stockster-scraper:$IMAGE_TAG
docker tag stockster-dashboard:$IMAGE_TAG $REGISTRY/stockster-dashboard:$IMAGE_TAG
docker tag stockster-api:$IMAGE_TAG $REGISTRY/stockster-api:$IMAGE_TAG

# Also tag as latest
docker tag stockster-scraper:$IMAGE_TAG $REGISTRY/stockster-scraper:latest
docker tag stockster-dashboard:$IMAGE_TAG $REGISTRY/stockster-dashboard:latest
docker tag stockster-api:$IMAGE_TAG $REGISTRY/stockster-api:latest

echo "Logging in to GitHub Container Registry..."
echo "Please ensure you have a GitHub Personal Access Token with 'write:packages' scope"
echo "If not logged in, run: echo \$GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USER --password-stdin"

# Push to registry
echo "Pushing images to $REGISTRY..."
docker push $REGISTRY/stockster-scraper:$IMAGE_TAG
docker push $REGISTRY/stockster-dashboard:$IMAGE_TAG
docker push $REGISTRY/stockster-api:$IMAGE_TAG
docker push $REGISTRY/stockster-scraper:latest
docker push $REGISTRY/stockster-dashboard:latest
docker push $REGISTRY/stockster-api:latest

echo ""
echo "✓ Images built and pushed successfully!"
echo "  - $REGISTRY/stockster-scraper:$IMAGE_TAG"
echo "  - $REGISTRY/stockster-dashboard:$IMAGE_TAG"
echo "  - $REGISTRY/stockster-scraper:latest"
echo "  - $REGISTRY/stockster-dashboard:latest"
echo ""
echo "To deploy this version to Kubernetes:"
echo "  kubectl set image deployment/stockster-dashboard dashboard=$REGISTRY/stockster-dashboard:$IMAGE_TAG -n stockster"
echo "  kubectl set image cronjob/stockster-scraper scraper=$REGISTRY/stockster-scraper:$IMAGE_TAG -n stockster"
echo ""
echo "Or update kustomization.yaml and run:"
echo "  sed -i 's|newTag:.*|newTag: $IMAGE_TAG|g' k8s/kustomization.yaml"
echo "  kubectl apply -k k8s/"
