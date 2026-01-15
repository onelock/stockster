#!/bin/bash
set -e

NAMESPACE="stockster"
REGISTRY="ghcr.io/onelock"

echo "=== Stockster Deployment Script ==="
echo ""

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "Namespace $NAMESPACE does not exist. Creating..."
    kubectl create namespace $NAMESPACE
fi

# Check deployment status
echo "Current deployment status:"
echo "---"
kubectl get all -n $NAMESPACE 2>/dev/null || echo "No resources deployed yet"
echo ""

# Deployment options
echo "Deployment options:"
echo "  1) Full deployment (namespace, secrets, PostgreSQL, apps)"
echo "  2) Update images only (specify version)"
echo "  3) Apply k8s manifests only"
echo ""
read -p "Select option [1-3]: " OPTION

case $OPTION in
    1)
        echo ""
        echo "=== Full Deployment ==="
        
        # Check for required secrets
        echo "Checking secrets..."
        if ! kubectl get secret ghcr-secret -n $NAMESPACE &> /dev/null; then
            echo "⚠️  ghcr-secret not found"
            read -p "Enter GitHub username [onelock]: " GH_USER
            GH_USER=${GH_USER:-onelock}
            read -sp "Enter GitHub token (PAT with packages:read): " GH_TOKEN
            echo ""
            kubectl create secret docker-registry ghcr-secret \
                --docker-server=ghcr.io \
                --docker-username=$GH_USER \
                --docker-password=$GH_TOKEN \
                --namespace=$NAMESPACE
            echo "✓ ghcr-secret created"
        else
            echo "✓ ghcr-secret exists"
        fi
        
        if ! kubectl get secret postgres-secret -n $NAMESPACE &> /dev/null; then
            echo "⚠️  postgres-secret not found"
            read -sp "Enter PostgreSQL password: " PG_PASSWORD
            echo ""
            kubectl create secret generic postgres-secret \
                --from-literal=username=stockster \
                --from-literal=password=$PG_PASSWORD \
                --from-literal=database=stockster \
                --from-literal=host=postgres \
                --from-literal=port=5432 \
                --namespace=$NAMESPACE
            echo "✓ postgres-secret created"
        else
            echo "✓ postgres-secret exists"
        fi
        
        echo ""
        echo "Deploying all resources..."
        kubectl apply -k k8s/
        
        echo ""
        echo "Waiting for PostgreSQL to be ready..."
        kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=3m || true
        
        echo ""
        echo "Waiting for dashboard deployment..."
        kubectl rollout status deployment/stockster-dashboard -n $NAMESPACE --timeout=3m || true
        
        echo ""
        echo "✓ Full deployment complete!"
        ;;
        
    2)
        echo ""
        # Get current versions
        echo "Current image versions:"
        CURRENT_DASHBOARD=$(kubectl get deployment stockster-dashboard -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "Not deployed")
        CURRENT_SCRAPER=$(kubectl get cronjob stockster-scraper -n $NAMESPACE -o jsonpath='{.spec.jobTemplate.spec.template.spec.containers[0].image}' 2>/dev/null || echo "Not deployed")
        echo "  Dashboard: $CURRENT_DASHBOARD"
        echo "  Scraper:   $CURRENT_SCRAPER"
        echo ""
        
        read -p "Enter image tag to deploy (e.g., 'latest' or 'main-abc1234'): " IMAGE_TAG
        
        if [ -z "$IMAGE_TAG" ]; then
            echo "Error: No image tag provided"
            exit 1
        fi
        
        echo ""
        echo "Deploying version: $IMAGE_TAG"
        
        # Update dashboard deployment
        echo "Updating dashboard..."
        kubectl set image deployment/stockster-dashboard \
            dashboard=$REGISTRY/stockster-dashboard:$IMAGE_TAG \
            -n $NAMESPACE \
            --record
        
        # Update scraper cronjob
        echo "Updating scraper..."
        kubectl set image cronjob/stockster-scraper \
            scraper=$REGISTRY/stockster-scraper:$IMAGE_TAG \
            -n $NAMESPACE \
            --record
        
        echo ""
        echo "Waiting for rollout..."
        kubectl rollout status deployment/stockster-dashboard -n $NAMESPACE --timeout=3m
        
        echo ""
        echo "✓ Images updated to version: $IMAGE_TAG"
        ;;
        
    3)
        echo ""
        echo "Applying k8s manifests..."
        kubectl apply -k k8s/
        echo "✓ Manifests applied"
        ;;
        
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "=== Deployment Summary ==="
kubectl get all -n $NAMESPACE
echo ""
echo "Useful commands:"
echo "  View logs:     kubectl logs -f -n $NAMESPACE -l app=stockster-dashboard"
echo "  View scraper:  kubectl get jobs -n $NAMESPACE -l app=stockster-scraper"
echo "  Check DB:      kubectl exec -it postgres-0 -n $NAMESPACE -- psql -U stockster -d stockster"
echo "  Rollback:      ./rollback.sh"
echo ""
