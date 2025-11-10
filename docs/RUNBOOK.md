# Operations Runbook

> Operational procedures, troubleshooting, and maintenance for Pulse AI Studio

---

## Table of Contents

1. [Access & Credentials](#access--credentials)
2. [Common Operations](#common-operations)
3. [Incident Response](#incident-response)
4. [Maintenance Procedures](#maintenance-procedures)
5. [Monitoring & Alerts](#monitoring--alerts)
6. [Troubleshooting](#troubleshooting)
7. [Disaster Recovery](#disaster-recovery)

---

## Access & Credentials

### AWS Console Access

- **Account ID:** [To be configured]
- **Region:** eu-central-1 (primary)
- **IAM Users:** Use SSO or federated access (recommended)
- **MFA:** Required for all admin accounts

### Service Endpoints

- **Frontend:** `https://app.your-domain.tld` or ALB DNS
- **Backend API:** `https://api.your-domain.tld/v1` or ALB path `/api/v1`
- **Gateway API:** `https://gateway.your-domain.tld/v1` or ALB path `/gateway/v1`
- **Swagger Docs:** `/docs` on each service

### Secret Access

All secrets stored in AWS Secrets Manager:

```bash
# List all secrets
aws secretsmanager list-secrets --region eu-central-1

# Get specific secret
aws secretsmanager get-secret-value --secret-id AI_STUDIO_DATABASE_URL --region eu-central-1
```

**Critical Secrets:**
- `AI_STUDIO_DATABASE_URL`
- `AI_STUDIO_REDIS_URL`
- `AI_STUDIO_JWT_SECRET`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `HYPERPAY_API_KEY`

---

## Common Operations

### 1. Deploy New Version

**Via GitHub Actions (Recommended):**
```bash
# Push to main branch triggers automatic deployment
git push origin main

# Or manually trigger workflow
gh workflow run app.yml
```

**Manual Deployment:**
```bash
# Update ECS services with new image
cd scripts
./update_ecs_images.sh <git-sha>
```

### 2. Rotate Secrets

**API Keys:**
```bash
# Update secret in Secrets Manager
aws secretsmanager update-secret \
  --secret-id OPENAI_API_KEY \
  --secret-string "new-key-value" \
  --region eu-central-1

# Restart ECS services to pick up new secret
aws ecs update-service \
  --cluster ai-studio-cluster \
  --service ai-studio-gateway \
  --force-new-deployment \
  --region eu-central-1
```

**JWT Secret:**
```bash
# Generate new secret
NEW_JWT_SECRET=$(openssl rand -hex 32)

# Update Secrets Manager
aws secretsmanager update-secret \
  --secret-id AI_STUDIO_JWT_SECRET \
  --secret-string "$NEW_JWT_SECRET" \
  --region eu-central-1

# Restart backend service
aws ecs update-service \
  --cluster ai-studio-cluster \
  --service ai-studio-backend \
  --force-new-deployment \
  --region eu-central-1
```

### 3. Scale Services

**Manual Scaling:**
```bash
# Scale up gateway service
aws ecs update-service \
  --cluster ai-studio-cluster \
  --service ai-studio-gateway \
  --desired-count 4 \
  --region eu-central-1
```

**Auto-Scaling Adjustment:**
```bash
# Update target tracking scaling policy
aws application-autoscaling put-scaling-policy \
  --policy-name gateway-cpu-scaling \
  --service-namespace ecs \
  --resource-id service/ai-studio-cluster/ai-studio-gateway \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

### 4. View Logs

**CloudWatch Logs:**
```bash
# Tail backend logs
aws logs tail /ecs/ai-studio-backend --follow --region eu-central-1

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/ai-studio-backend \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000 \
  --region eu-central-1
```

**Search by trace_id:**
```bash
aws logs filter-log-events \
  --log-group-name /ecs/ai-studio-gateway \
  --filter-pattern '{ $.trace_id = "abc123" }' \
  --region eu-central-1
```

### 5. Database Operations

**Connect to Database:**
```bash
# Get DB endpoint
DB_HOST=$(aws rds describe-db-clusters \
  --db-cluster-identifier ai-studio-db \
  --query 'DBClusters[0].Endpoint' \
  --output text \
  --region eu-central-1)

# Get credentials from Secrets Manager
DB_CREDS=$(aws secretsmanager get-secret-value \
  --secret-id AI_STUDIO_DATABASE_URL \
  --query SecretString \
  --output text \
  --region eu-central-1)

# Connect via psql (from bastion or ECS Exec)
psql "$DB_CREDS"
```

**Run Migrations:**
```bash
# SSH into backend container (or use ECS Exec)
aws ecs execute-command \
  --cluster ai-studio-cluster \
  --task <task-id> \
  --container backend \
  --interactive \
  --command "/bin/bash"

# Inside container
cd /app
alembic upgrade head
```

### 6. Clear Stuck Jobs

```sql
-- Connect to database
-- Find stuck jobs (processing > 1 hour)
SELECT * FROM jobs 
WHERE status = 'processing' 
AND updated_at < NOW() - INTERVAL '1 hour';

-- Reset to pending (worker will retry)
UPDATE jobs 
SET status = 'pending', updated_at = NOW()
WHERE status = 'processing' 
AND updated_at < NOW() - INTERVAL '1 hour';

-- Or mark as failed
UPDATE jobs 
SET status = 'failed', updated_at = NOW()
WHERE status = 'processing' 
AND updated_at < NOW() - INTERVAL '1 hour';
```

### 7. Throttle Abusive Users

**Temporary Rate Limit:**
```bash
# Block user in Redis (rate limit key)
redis-cli -h <redis-endpoint>
> SET ratelimit:block:<user-id> 1 EX 3600
```

**Permanent Ban:**
```sql
-- Deactivate user account
UPDATE users SET is_active = FALSE WHERE id = '<user-id>';
```

---

## Incident Response

### Severity Levels

- **P0 (Critical):** Complete service outage, data loss, security breach
- **P1 (High):** Major feature unavailable, performance degradation
- **P2 (Medium):** Minor feature broken, intermittent errors
- **P3 (Low):** Cosmetic issues, enhancement requests

### P0/P1 Incident Response

1. **Acknowledge** (within 15 minutes)
   - Notify team via Slack/email
   - Create incident document

2. **Assess** (within 30 minutes)
   - Check CloudWatch dashboards
   - Review recent deployments (ACTIVITY.md)
   - Check ALB target health
   - Review error logs

3. **Mitigate**
   - Rollback deployment if recent change
   - Scale up services if capacity issue
   - Failover to backup region (if configured)
   - Enable maintenance mode (if needed)

4. **Resolve**
   - Fix root cause
   - Deploy patch
   - Verify health checks
   - Monitor for 30 minutes

5. **Post-Mortem** (within 24 hours)
   - Document timeline
   - Identify root cause
   - List action items
   - Update runbook

### Rollback Procedure

```bash
# List recent task definition revisions
aws ecs list-task-definitions \
  --family-prefix ai-studio-backend \
  --sort DESC \
  --max-items 5

# Rollback to previous revision
aws ecs update-service \
  --cluster ai-studio-cluster \
  --service ai-studio-backend \
  --task-definition ai-studio-backend:42 \
  --region eu-central-1

# Wait for service stability
aws ecs wait services-stable \
  --cluster ai-studio-cluster \
  --services ai-studio-backend \
  --region eu-central-1
```

---

## Maintenance Procedures

### Planned Maintenance Window

**Schedule:** Sunday 02:00-04:00 UTC (low traffic period)

**Pre-Maintenance:**
1. Notify users via email/app banner (48 hours notice)
2. Take database snapshot
3. Document current service versions
4. Prepare rollback plan

**During Maintenance:**
1. Enable maintenance mode (optional)
2. Apply updates (Terraform, database migrations, deployments)
3. Run smoke tests
4. Verify all services healthy

**Post-Maintenance:**
1. Monitor for 1 hour
2. Disable maintenance mode
3. Send all-clear notification
4. Update ACTIVITY.md

### Database Backup & Restore

**Manual Snapshot:**
```bash
# Create snapshot
aws rds create-db-cluster-snapshot \
  --db-cluster-snapshot-identifier ai-studio-manual-$(date +%Y%m%d-%H%M) \
  --db-cluster-identifier ai-studio-db \
  --region eu-central-1
```

**Restore from Snapshot:**
```bash
# Restore to new cluster
aws rds restore-db-cluster-from-snapshot \
  --db-cluster-identifier ai-studio-db-restored \
  --snapshot-identifier ai-studio-manual-20251110-0200 \
  --engine aurora-postgresql \
  --region eu-central-1

# Update backend to point to restored cluster (update DSN in Secrets Manager)
```

### Redis Maintenance

**Clear All Cache:**
```bash
redis-cli -h <redis-endpoint>
> FLUSHALL
```

**Clear Usage Cache (force DB sync):**
```bash
redis-cli -h <redis-endpoint>
> KEYS usage:*
> DEL usage:tokens:* usage:images:* usage:videos:*
```

---

## Monitoring & Alerts

### CloudWatch Dashboards

- **Service Health:** `ai-studio-service-health`
- **Usage Metrics:** `ai-studio-usage`
- **Latency:** `ai-studio-latency`
- **Costs:** `ai-studio-costs`

### Critical Alarms

| Alarm | Threshold | Action |
|-------|-----------|--------|
| ALB 5xx Errors | > 10 in 5 min | Check ECS task health, review logs |
| ECS Unhealthy Tasks | > 0 | Check task logs, restart tasks |
| RDS CPU | > 80% for 5 min | Scale up ACUs, optimize queries |
| Redis CPU | > 80% for 5 min | Scale up node type, review usage |
| Disk Space | > 80% | Clean up old files, expand storage |
| OpenAI API Errors | > 5% | Check API status, use fallback |

### Health Check Endpoints

```bash
# Backend health
curl https://api.your-domain.tld/v1/health

# Gateway health
curl https://gateway.your-domain.tld/v1/health

# Expected response: {"status": "healthy", "timestamp": "..."}
```

---

## Troubleshooting

### Service Won't Start

**Check ECS Task Logs:**
```bash
aws logs tail /ecs/ai-studio-backend --follow --region eu-central-1
```

**Common Issues:**
- Secrets Manager access denied → Check task IAM role
- Database unreachable → Check security group rules
- Image pull failed → Check ECR permissions

### High Latency

**Check Gateway Response Times:**
```bash
# CloudWatch Insights query
fields @timestamp, latency_ms
| filter @message like /POST \/v1\/chat\/complete/
| stats avg(latency_ms), max(latency_ms), p95(latency_ms)
```

**Common Causes:**
- OpenAI API slow → Check provider status page
- Database slow queries → Review query execution plans
- Cold start (first request after idle) → Keep min tasks > 0

### Usage Not Updating

**Check Redis Connection:**
```bash
redis-cli -h <redis-endpoint> PING
# Expected: PONG
```

**Check Gateway Logs:**
```bash
aws logs filter-log-events \
  --log-group-name /ecs/ai-studio-gateway \
  --filter-pattern "usage_meter" \
  --region eu-central-1
```

**Sync Redis → DB:**
```python
# Run from backend container
python -m scripts.sync_usage_to_db
```

### Payment Webhook Not Received

**Check Worker Logs:**
```bash
aws logs tail /ecs/ai-studio-worker --follow --region eu-central-1
```

**Check Payment Provider Logs:**
- HyperPay dashboard → Webhooks section
- Verify webhook URL configured correctly
- Check signature validation logs

**Manual Payment Activation:**
```sql
-- Connect to database
UPDATE subscriptions 
SET status = 'active', renews_at = NOW() + INTERVAL '30 days'
WHERE user_id = '<user-id>' AND status = 'pending';
```

### SES Emails Not Sending

**Check SES Sandbox Status:**
```bash
aws ses get-account-sending-enabled --region eu-central-1
```

**Verify Email Identity:**
```bash
aws ses list-identities --region eu-central-1
aws ses get-identity-verification-attributes \
  --identities your-email@domain.com \
  --region eu-central-1
```

**Check Backend Logs:**
```bash
aws logs filter-log-events \
  --log-group-name /ecs/ai-studio-backend \
  --filter-pattern "SES" \
  --region eu-central-1
```

---

## Disaster Recovery

### Data Loss Scenarios

**Database Corruption:**
1. Stop all writes (disable backend service)
2. Restore from latest automated snapshot
3. Apply transaction logs if available (point-in-time recovery)
4. Verify data integrity
5. Resume service

**S3 Bucket Deleted:**
1. Enable S3 versioning (preventive measure)
2. Restore from backup (if configured)
3. Contact AWS support for assistance

**Complete Region Failure:**
1. Failover to backup region (if multi-region configured)
2. Update DNS to point to backup region
3. Monitor backup region capacity
4. Plan migration back to primary region

### Backup Strategy

**Automated Backups:**
- Aurora: Daily snapshots (retained 7 days)
- S3: Versioning enabled (retained 30 days)
- Terraform state: S3 versioning enabled

**Manual Backups (before major changes):**
```bash
# Database snapshot
aws rds create-db-cluster-snapshot \
  --db-cluster-snapshot-identifier ai-studio-pre-migration-$(date +%Y%m%d) \
  --db-cluster-identifier ai-studio-db

# S3 backup
aws s3 sync s3://ai-studio-assets s3://ai-studio-backup-assets
```

### Recovery Time Objectives (RTO/RPO)

- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 1 hour (automated snapshots)

---

## Contacts

- **On-Call Engineer:** [To be defined]
- **AWS Support:** [Support plan tier]
- **HyperPay Support:** [Contact details]
- **Escalation Path:** [Define escalation chain]

---

*This runbook should be reviewed and updated quarterly. All incidents should result in runbook updates.*
