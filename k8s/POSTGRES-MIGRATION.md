# PostgreSQL Migration Guide

## Overview
This guide helps you migrate from SQLite to PostgreSQL for production deployment.

## Changes Made

### 1. New Files
- `k8s/postgres-statefulset.yaml` - PostgreSQL deployment
- `k8s/postgres-secret.yaml` - Database credentials
- `di_scraper/db_utils.py` - Database abstraction layer

### 2. Updated Files
- `k8s/cronjob.yaml` - Uses PostgreSQL env vars
- `k8s/dashboard-deployment.yaml` - Uses PostgreSQL env vars
- `k8s/kustomization.yaml` - Includes PostgreSQL resources
- `di_scraper/scrape_di.py` - Uses db_utils for connection
- `requirements.txt` - Added psycopg2-binary

## Pre-Deployment Steps

### 1. Update PostgreSQL Password
Edit `k8s/postgres-secret.yaml` and change the password:
```bash
# Generate a strong password
openssl rand -base64 32

# Update the password in k8s/postgres-secret.yaml
```

### 2. Build and Push New Images
```bash
# Your scraper and dashboard now support both SQLite and PostgreSQL
./build-and-push.sh
```

### 3. Create GitHub Container Registry Secret
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=onelock \
  --docker-password=YOUR_GITHUB_TOKEN \
  --namespace=stockster
```

## Deployment

### Deploy Everything
```bash
# Deploy namespace, PostgreSQL, secrets, scraper, and dashboard
kubectl apply -k k8s/

# Verify deployment
kubectl get all -n stockster
kubectl get pvc -n stockster
```

### Check PostgreSQL Status
```bash
# Check if PostgreSQL is running
kubectl get pods -n stockster -l app=postgres

# View PostgreSQL logs
kubectl logs -n stockster -l app=postgres

# Connect to PostgreSQL (optional)
kubectl exec -it postgres-0 -n stockster -- psql -U stockster -d stockster
```

## Migration from Existing SQLite Data (Optional)

If you have existing SQLite data you want to migrate:

```bash
# 1. Export SQLite data to CSV
sqlite3 db/stocks_db.db <<EOF
.headers on
.mode csv
.output trading.csv
SELECT * FROM stocks_trading;
.output historical.csv
SELECT * FROM stocks_historical;
.output metrics.csv
SELECT * FROM stocks_metrics;
EOF

# 2. Copy CSV files to PostgreSQL pod
kubectl cp trading.csv stockster/postgres-0:/tmp/
kubectl cp historical.csv stockster/postgres-0:/tmp/
kubectl cp metrics.csv stockster/postgres-0:/tmp/

# 3. Import into PostgreSQL
kubectl exec -it postgres-0 -n stockster -- bash
psql -U stockster -d stockster <<EOF
\copy stocks_trading FROM '/tmp/trading.csv' WITH CSV HEADER;
\copy stocks_historical FROM '/tmp/historical.csv' WITH CSV HEADER;
\copy stocks_metrics FROM '/tmp/metrics.csv' WITH CSV HEADER;
EOF
```

## Rollback to SQLite

If you need to rollback:

```bash
# 1. Scale down current deployment
kubectl scale deployment stockster-dashboard --replicas=0 -n stockster
kubectl delete cronjob stockster-scraper -n stockster

# 2. Revert manifests to use SQLite
# - Change env vars back to DB_PATH
# - Add back volume mounts
# - Remove PostgreSQL env vars

# 3. Redeploy
kubectl apply -k k8s/
```

## Monitoring

```bash
# Watch all pods
watch kubectl get pods -n stockster

# Check logs
kubectl logs -f -n stockster -l app=stockster-dashboard
kubectl logs -n stockster -l app=stockster-scraper

# Check PostgreSQL resource usage
kubectl top pod -n stockster postgres-0
```

## Troubleshooting

### Connection Refused
- Ensure PostgreSQL pod is running: `kubectl get pods -n stockster`
- Check service: `kubectl get svc -n stockster postgres`
- Verify secret exists: `kubectl get secret -n stockster postgres-secret`

### Authentication Failed
- Check password in secret: `kubectl get secret postgres-secret -n stockster -o yaml`
- Recreate secret if needed

### Performance Issues
- Increase PostgreSQL resources in `postgres-statefulset.yaml`
- Add connection pooling (PgBouncer) if needed

## Backup Strategy

### Automated Backups
```bash
# Create a CronJob for daily backups
kubectl create cronjob postgres-backup \
  --image=postgres:16-alpine \
  --schedule="0 2 * * *" \
  --namespace=stockster \
  -- /bin/sh -c "pg_dump -h postgres -U stockster stockster > /backup/stockster-\$(date +%Y%m%d).sql"
```

### Manual Backup
```bash
# Backup to local file
kubectl exec postgres-0 -n stockster -- \
  pg_dump -U stockster stockster > backup-$(date +%Y%m%d).sql

# Restore from backup
kubectl exec -i postgres-0 -n stockster -- \
  psql -U stockster stockster < backup-20260115.sql
```
