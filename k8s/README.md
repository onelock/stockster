# GitHub Container Registry Setup

## Prerequisites
1. Create a GitHub Personal Access Token (PAT):
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scope: `write:packages` (includes read)
   - Copy the token

## Login to GitHub Container Registry

```bash
export GITHUB_TOKEN=your_github_pat_token
export GITHUB_USER=onelock

echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USER --password-stdin
```

## Build and Push Images

```bash
# Set your GitHub username
export GITHUB_USER=onelock

# Build and push
./build-and-push.sh
```

## Configure Kubernetes to Pull Images

Create an image pull secret:

```bash
kubectl create secret docker-registry ghcr-secret \
  --namespace=stockster \
  --docker-server=ghcr.io \
  --docker-username=$GITHUB_USER \
  --docker-password=$GITHUB_TOKEN
```

The deployments will automatically use this secret.

## Make Images Public (Optional)

To avoid needing image pull secrets:

1. Go to your GitHub profile → Packages
2. Find `stockster-scraper` and `stockster-dashboard`
3. Click Package Settings
4. Change visibility to "Public"

## Deploy to Kubernetes

```bash
kubectl apply -k k8s/
```
