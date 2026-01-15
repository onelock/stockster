# CI/CD Setup Guide

## GitHub Secrets Required

Add these secrets in your GitHub repository: **Settings → Secrets and variables → Actions → New repository secret**

### 1. KUBE_CONFIG
Your Kubernetes config file (base64 encoded).

**Generate it:**
```bash
# From your k3s server (or wherever you have kubectl access)
cat ~/.kube/config | base64 -w 0
```

Copy the output and paste it as the `KUBE_CONFIG` secret value.

**Important:** Make sure to update the server address in your kubeconfig from `127.0.0.1:6443` to your actual server IP before encoding:
```bash
# Edit the config
vi ~/.kube/config
# Change: server: https://127.0.0.1:6443
# To: server: https://YOUR_SERVER_IP:6443

# Then encode
cat ~/.kube/config | base64 -w 0
```

### 2. POSTGRES_PASSWORD
Your PostgreSQL database password (the one you set in k8s/postgres-secret.yaml).

**Generate a strong password:**
```bash
openssl rand -base64 32
```

Save this password:
- As GitHub Secret: `POSTGRES_PASSWORD`
- Update it in `k8s/postgres-secret.yaml` if deploying manually

## Workflow Triggers

The workflow runs automatically on:
- **Push to main branch** - Full build and deploy

## What the Workflow Does

1. ✅ **Build Images**
   - Builds scraper and dashboard Docker images
   - Pushes to GitHub Container Registry (ghcr.io)
   - Tags with commit SHA and `latest`

2. ✅ **Setup Kubernetes**
   - Creates namespace `stockster` (if not exists)
   - Creates/updates `ghcr-secret` for pulling images
   - Creates/updates `postgres-secret` with DB credentials

3. ✅ **Deploy Infrastructure**
   - Deploys PostgreSQL StatefulSet
   - Deploys PVC for database storage
   - Waits for PostgreSQL to be ready

4. ✅ **Deploy Applications**
   - Updates dashboard deployment with new image
   - Updates scraper cronjob with new image
   - Waits for rollout completion

5. ✅ **Creates Summary**
   - Shows deployment details in GitHub Actions UI

## Manual Deployment

If you need to deploy manually:

```bash
# 1. Build and push images
docker build -f Dockerfile.scraper -t ghcr.io/onelock/stockster-scraper:latest .
docker build -f Dockerfile.dashboard -t ghcr.io/onelock/stockster-dashboard:latest .
docker push ghcr.io/onelock/stockster-scraper:latest
docker push ghcr.io/onelock/stockster-dashboard:latest

# 2. Create namespace
kubectl create namespace stockster

# 3. Create secrets
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=onelock \
  --docker-password=YOUR_GITHUB_TOKEN \
  --namespace=stockster

kubectl create secret generic postgres-secret \
  --from-literal=username=stockster \
  --from-literal=password=YOUR_POSTGRES_PASSWORD \
  --from-literal=database=stockster \
  --from-literal=host=postgres \
  --from-literal=port=5432 \
  --namespace=stockster

# 4. Deploy everything
kubectl apply -k k8s/
```

## Monitoring Deployments

View workflow runs:
- Go to **Actions** tab in GitHub
- Click on the latest workflow run
- View logs and deployment summary

Check deployment status:
```bash
# Watch all resources
kubectl get all -n stockster

# View pod logs
kubectl logs -f -n stockster -l app=stockster-dashboard
kubectl logs -n stockster $(kubectl get jobs -n stockster -l app=stockster-scraper -o jsonpath='{.items[0].metadata.name}') -c scraper

# Check PostgreSQL
kubectl logs -n stockster postgres-0
```

## Rollback

If a deployment fails:

```bash
# Rollback dashboard
kubectl rollout undo deployment/stockster-dashboard -n stockster

# Delete failed scraper jobs
kubectl delete jobs -n stockster -l app=stockster-scraper

# Or use the rollback script
./rollback.sh
```

## Troubleshooting

### Workflow fails at "Configure kubectl"
- Check that `KUBE_CONFIG` secret is correctly base64 encoded
- Verify the server address in kubeconfig is accessible from GitHub Actions runners

### Workflow fails at "Create or update ghcr-secret"
- `GITHUB_TOKEN` is automatically provided by GitHub Actions
- No action needed if you see "forbidden" - check repository permissions

### Workflow fails at "Deploy to staging"
- Check that images were successfully pushed
- Verify namespace exists: `kubectl get ns stockster`
- Check pod status: `kubectl get pods -n stockster`

### Images not pulling
- Verify ghcr-secret exists: `kubectl get secret ghcr-secret -n stockster`
- Check image registry is accessible
- Make sure GitHub packages visibility is correct (public or private with proper credentials)

## Security Notes

1. **Never commit secrets** - Use GitHub Secrets only
2. **Rotate credentials** periodically (POSTGRES_PASSWORD, GITHUB_TOKEN)
3. **Limit kubeconfig permissions** - Create a service account with minimal permissions
4. **Use separate environments** - Consider separate namespaces for staging/production

## Advanced: Service Account for CI/CD

For better security, create a dedicated service account:

```bash
# Create service account
kubectl create serviceaccount github-deployer -n stockster

# Create role with necessary permissions
kubectl create role deployer --verb=get,list,watch,create,update,patch,delete \
  --resource=deployments,cronjobs,services,secrets,pods,statefulsets,pvc \
  -n stockster

# Bind role to service account
kubectl create rolebinding deployer-binding \
  --role=deployer \
  --serviceaccount=stockster:github-deployer \
  -n stockster

# Get service account token and create kubeconfig
# (Use this instead of your personal kubeconfig)
```
