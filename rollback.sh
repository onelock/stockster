#!/bin/bash
set -e

NAMESPACE="stockster"

echo "Rolling back dashboard deployment..."

# Rollback to previous version
kubectl rollout undo deployment/stockster-dashboard -n $NAMESPACE

# Check rollout status
kubectl rollout status deployment/stockster-dashboard -n $NAMESPACE

echo ""
echo "✓ Rollback complete!"
echo ""
echo "Current image version:"
kubectl get deployment stockster-dashboard -n $NAMESPACE \
    -o jsonpath='{.spec.template.spec.containers[0].image}'
echo -e "\n"

echo "Rollout history:"
kubectl rollout history deployment/stockster-dashboard -n $NAMESPACE
