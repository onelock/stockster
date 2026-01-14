# Deployment Guide - Rolling Updates & Rollbacks

## Image Versioning Strategy

Images are tagged with:
- **Git commit SHA** (e.g., `a3f2b1c`) - unique identifier for each build
- **`latest`** - always points to most recent build

Format: `ghcr.io/onelock/stockster-scraper:a3f2b1c`

## Build and Push New Version

```bash
# Commit your changes first
git add .
git commit -m "Your changes"

# Build and push (creates version based on git SHA)
./build-and-push.sh
```

This will output:
```
Using git commit SHA: a3f2b1c
✓ Images built and pushed successfully!
  - ghcr.io/onelock/stockster-scraper:a3f2b1c
  - ghcr.io/onelock/stockster-dashboard:a3f2b1c
```

## Deploy New Version

### Option 1: Interactive Deploy Script
```bash
./deploy.sh
# Enter the image tag when prompted (e.g., a3f2b1c)
```

### Option 2: Manual Deployment
```bash
IMAGE_TAG=a3f2b1c

# Update dashboard
kubectl set image deployment/stockster-dashboard \
  dashboard=ghcr.io/onelock/stockster-dashboard:$IMAGE_TAG \
  -n stockster

# Update scraper cronjob
kubectl set image cronjob/stockster-scraper \
  scraper=ghcr.io/onelock/stockster-scraper:$IMAGE_TAG \
  -n stockster
```

### Option 3: GitOps with Kustomize
```bash
IMAGE_TAG=a3f2b1c

# Update kustomization
sed -i "s|newTag:.*|newTag: $IMAGE_TAG|g" k8s/kustomization.yaml

# Commit and apply
git add k8s/kustomization.yaml
git commit -m "Deploy version $IMAGE_TAG"
kubectl apply -k k8s/
```

## Monitor Rollout

```bash
# Watch rollout status
kubectl rollout status deployment/stockster-dashboard -n stockster

# Check pod status
kubectl get pods -n stockster -w

# View logs of new pods
kubectl logs -f deployment/stockster-dashboard -n stockster
```

## Rollback

### Quick Rollback (to previous version)
```bash
./rollback.sh
```

### Manual Rollback
```bash
# Undo to previous revision
kubectl rollout undo deployment/stockster-dashboard -n stockster

# Rollback to specific revision
kubectl rollout history deployment/stockster-dashboard -n stockster
kubectl rollout undo deployment/stockster-dashboard --to-revision=3 -n stockster
```

### Rollback to Specific Version
```bash
IMAGE_TAG=a3f2b1c  # Known good version
kubectl set image deployment/stockster-dashboard \
  dashboard=ghcr.io/onelock/stockster-dashboard:$IMAGE_TAG \
  -n stockster
```

## View Deployment History

```bash
# Show all revisions
kubectl rollout history deployment/stockster-dashboard -n stockster

# Show specific revision details
kubectl rollout history deployment/stockster-dashboard --revision=2 -n stockster

# Current image version
kubectl get deployment stockster-dashboard -n stockster \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

## Pause/Resume Rollout

```bash
# Pause (to investigate issues before full rollout)
kubectl rollout pause deployment/stockster-dashboard -n stockster

# Resume
kubectl rollout resume deployment/stockster-dashboard -n stockster
```

## CI/CD Integration Example

### GitHub Actions
```yaml
name: Deploy to K8s

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to GHCR
        run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
      
      - name: Build and Push
        run: ./build-and-push.sh
      
      - name: Deploy to K8s
        run: |
          IMAGE_TAG=$(git rev-parse --short HEAD)
          kubectl set image deployment/stockster-dashboard \
            dashboard=ghcr.io/${{ github.repository_owner }}/stockster-dashboard:$IMAGE_TAG \
            -n stockster
```

## Best Practices

1. **Always test in staging** before production
2. **Keep 5 revisions** for easy rollback (already configured)
3. **Monitor metrics** after deployment
4. **Tag releases** in git for production versions
5. **Use semantic versioning** for major releases (e.g., v1.0.0)
6. **Document breaking changes** in commit messages
