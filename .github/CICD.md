# CI/CD Pipeline Setup Guide

## Overview

The CI/CD pipeline consists of 4 GitHub Actions workflows:

1. **CI** (`ci.yml`) - Lint, test, and build images on every push/PR
2. **Auto Deploy Staging** (`auto-deploy-staging.yml`) - Automatically deploy to staging when pushing to `main`
3. **Manual Deploy** (`deploy.yml`) - Manually deploy specific versions to staging/production
4. **Rollback** (`rollback.yml`) - Quickly rollback deployments

## Prerequisites

### 1. Set up GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

#### `KUBE_CONFIG` (Required)
Your Kubernetes config file, base64 encoded:

```bash
cat ~/.kube/config | base64 | pbcopy  # macOS
cat ~/.kube/config | base64 -w 0 | xclip  # Linux
```

Paste the output as the secret value.

#### Optional Secrets (for notifications):
- `SLACK_WEBHOOK_URL` - For Slack notifications
- `DISCORD_WEBHOOK_URL` - For Discord notifications

### 2. Create GitHub Environments

Go to Settings → Environments and create:

- **staging** - No protection rules needed
- **production** - Add protection rules:
  - ✓ Required reviewers (add team members)
  - ✓ Wait timer: 5 minutes
  - ✓ Deployment branches: Only `main`

### 3. Enable GitHub Actions

Go to Settings → Actions → General:
- ✓ Allow all actions
- ✓ Read and write permissions
- ✓ Allow GitHub Actions to create pull requests

## Workflows

### 1. CI - Continuous Integration

**Trigger**: Push or PR to `main` or `develop`

**Steps**:
1. Lint code with flake8
2. Check formatting with black
3. Run tests
4. Build Docker images (on push only)
5. Push to GitHub Container Registry

**Status**: View on GitHub Actions tab

### 2. Auto Deploy to Staging

**Trigger**: Automatic on push to `main` branch

**Steps**:
1. Build images tagged with `main-<sha>`
2. Push to registry
3. Deploy to `stockster-staging` namespace
4. Wait for rollout to complete

**Access staging**: `http://staging-stockster.yourdomain.com`

### 3. Manual Deploy (Production)

**Trigger**: Manual via GitHub Actions UI

**Usage**:
1. Go to Actions → "CD - Deploy to Kubernetes"
2. Click "Run workflow"
3. Select:
   - Environment: `production`
   - Image tag: `main-a3f2b1c` (or leave empty for latest)
4. Click "Run workflow"

**Review required** for production deployments.

### 4. Rollback

**Trigger**: Manual via GitHub Actions UI

**Usage**:
1. Go to Actions → "Rollback Deployment"
2. Click "Run workflow"
3. Select:
   - Environment: `staging` or `production`
   - Revision: (leave empty to rollback to previous)
4. Click "Run workflow"

## Workflow Examples

### Deploy new feature to staging
```bash
git checkout -b feature/new-dashboard
# Make changes
git commit -am "Add new dashboard feature"
git push origin feature/new-dashboard
# Create PR → After merge to main, auto-deploys to staging
```

### Promote staging to production
1. Verify staging works: `https://staging.yourdomain.com`
2. Go to Actions → "CD - Deploy to Kubernetes"
3. Run workflow:
   - Environment: `production`
   - Image tag: `main-a3f2b1c` (copy from staging deployment)
4. Approve deployment (if reviewers required)
5. Monitor deployment status

### Emergency rollback
1. Go to Actions → "Rollback Deployment"
2. Select environment: `production`
3. Leave revision empty (rolls back to previous)
4. Click "Run workflow"
5. Deployment reverts in ~1 minute

## Deployment Flow

```
┌─────────────┐
│   Develop   │
└──────┬──────┘
       │
       │ PR
       ▼
┌─────────────┐     Auto Deploy     ┌─────────────┐
│    Main     │────────────────────▶│   Staging   │
└──────┬──────┘                     └─────────────┘
       │                                    │
       │                                    │ Verify
       │                                    ▼
       │                            ┌─────────────┐
       │     Manual Deploy          │             │
       └───────────────────────────▶│ Production  │
                + Approval           │             │
                                     └─────────────┘
```

## Monitoring Deployments

### View workflow runs
```bash
# GitHub CLI
gh run list
gh run view <run-id>
gh run watch <run-id>
```

### Check deployment status
```bash
kubectl get deployments -n stockster-staging
kubectl rollout status deployment/stockster-dashboard -n stockster-staging
kubectl get pods -n stockster-staging
```

### View logs
```bash
kubectl logs -f deployment/stockster-dashboard -n stockster-staging
kubectl logs -f deployment/stockster-dashboard -n stockster-production
```

## Troubleshooting

### Build fails
- Check lint errors in GitHub Actions logs
- Run locally: `flake8 . && black --check .`
- Fix and commit

### Deployment fails
- Check `KUBE_CONFIG` secret is correctly set
- Verify namespace exists: `kubectl get ns`
- Check image exists: `docker pull ghcr.io/onelock/stockster-dashboard:main-abc123`

### Rollback doesn't work
- Check revision history: `kubectl rollout history deployment/stockster-dashboard -n stockster-production`
- Verify you have at least 2 revisions
- Manual rollback: `kubectl rollout undo deployment/stockster-dashboard -n stockster-production`

## Best Practices

1. **Test in staging first** - Always verify in staging before production
2. **Use feature branches** - Create PRs for code review
3. **Tag releases** - Tag production deployments: `git tag v1.0.0`
4. **Monitor after deploy** - Watch logs and metrics for 5-10 minutes
5. **Keep rollback ready** - Know how to quickly rollback if needed
6. **Document changes** - Add release notes for major deployments

## Advanced: Branch-based Environments

To deploy feature branches to ephemeral environments:

```yaml
# .github/workflows/preview-deploy.yml
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to preview
        run: |
          BRANCH_NAME=$(echo ${{ github.head_ref }} | sed 's/[^a-zA-Z0-9]/-/g')
          kubectl create namespace stockster-preview-$BRANCH_NAME || true
          # Deploy to stockster-preview-$BRANCH_NAME
```
