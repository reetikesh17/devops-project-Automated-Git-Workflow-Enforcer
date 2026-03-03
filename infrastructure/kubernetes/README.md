# Kubernetes Manifests - Git Workflow Enforcer

## Overview

This directory contains Kubernetes manifests for deploying the Git Workflow Enforcer with externalized configuration using ConfigMaps.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    ConfigMap                             │
│              (git-enforcer-config)                       │
│                                                          │
│  Contains validation rules (rules.json)                 │
│  - Branch patterns                                       │
│  - Commit message types                                  │
│  - Validation settings                                   │
└──────────────────────────────────────────────────────────┘
                          │
                          │ Mounted as Volume
                          ↓
┌──────────────────────────────────────────────────────────┐
│                  Kubernetes Workloads                    │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │    Job     │  │ Deployment │  │  CronJob   │        │
│  │            │  │            │  │            │        │
│  │ One-time   │  │ Continuous │  │ Scheduled  │        │
│  │ validation │  │ validation │  │ validation │        │
│  └────────────┘  └────────────┘  └────────────┘        │
│                                                          │
│  All read rules from mounted ConfigMap                  │
└──────────────────────────────────────────────────────────┘
```

## Files

| File | Description |
|------|-------------|
| `configmap.yaml` | ConfigMap with validation rules |
| `job.yaml` | One-time validation job |
| `deployment.yaml` | Continuous validation service |
| `cronjob.yaml` | Scheduled validation job |
| `service.yaml` | Service definition (optional) |
| `CONFIGMAP-GUIDE.md` | Detailed ConfigMap usage guide |
| `test-configmap.sh` | Test script for ConfigMap setup |

## Quick Start

### 1. Create ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 2. Deploy Job

```bash
kubectl apply -f job.yaml
```

### 3. Verify

```bash
# Check job status
kubectl get jobs

# View logs
kubectl logs -l app=git-workflow-enforcer

# Check ConfigMap
kubectl get configmap git-enforcer-config
```

## Deployment Options

### Option 1: Job (One-time Validation)

**Use Case**: Manual validation, CI/CD integration

```bash
kubectl apply -f job.yaml
```

**Features**:
- Runs once and completes
- 3 retry attempts on failure
- Auto-cleanup after 1 hour
- Uses ConfigMap for rules

### Option 2: Deployment (Continuous Service)

**Use Case**: Always-on validation service

```bash
kubectl apply -f deployment.yaml
```

**Features**:
- 1 replica (scalable)
- Health checks (liveness/readiness)
- Continuous validation
- Uses ConfigMap for rules

### Option 3: CronJob (Scheduled Validation)

**Use Case**: Daily validation checks

```bash
kubectl apply -f cronjob.yaml
```

**Features**:
- Runs daily at midnight
- Keeps history of last 3 successful jobs
- Prevents concurrent runs
- Uses ConfigMap for rules

### Option 4: Deploy All

```bash
kubectl apply -f .
```

## ConfigMap Management

### View ConfigMap

```bash
# List ConfigMaps
kubectl get configmap

# View details
kubectl describe configmap git-enforcer-config

# View rules.json
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq .
```

### Update ConfigMap

#### Method 1: Edit Directly

```bash
kubectl edit configmap git-enforcer-config
```

#### Method 2: Apply Updated File

```bash
# Edit configmap.yaml
nano configmap.yaml

# Apply changes
kubectl apply -f configmap.yaml
```

#### Method 3: Replace from File

```bash
kubectl delete configmap git-enforcer-config
kubectl create configmap git-enforcer-config --from-file=rules.json=new-rules.json
```

### Reload Configuration

**For Jobs** (immutable):
```bash
kubectl delete job git-workflow-enforcer-job
kubectl apply -f job.yaml
```

**For Deployments**:
```bash
kubectl rollout restart deployment git-workflow-enforcer
```

**For CronJobs** (next run):
```bash
# Or trigger manually
kubectl create job --from=cronjob/git-workflow-enforcer-cron manual-test
```

## Configuration Examples

### Default Configuration

```json
{
  "version": "1.0",
  "branches": {
    "patterns": {
      "feature": "^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$",
      "bugfix": "^bugfix/[A-Z]+-[0-9]+-[a-z0-9-]+$",
      "hotfix": "^hotfix/[A-Z]+-[0-9]+$",
      "release": "^release/v[0-9]+\\.[0-9]+\\.[0-9]+(-[a-z0-9]+)?$"
    },
    "protected": ["main", "master", "develop"],
    "ticketIdPattern": "[A-Z]+-[0-9]+"
  },
  "commits": {
    "types": ["feat", "fix", "chore", "docs", "refactor", "test", "ci"],
    "descriptionLength": {
      "min": 10,
      "max": 100
    },
    "enforceCase": "lowercase",
    "allowBreakingChanges": true
  }
}
```

### Strict Mode

```json
{
  "validation": {
    "strictMode": true,
    "blockOnWarning": true
  },
  "commits": {
    "descriptionLength": {
      "min": 20,
      "max": 72
    }
  }
}
```

### Relaxed Mode

```json
{
  "validation": {
    "strictMode": false,
    "blockOnWarning": false
  },
  "commits": {
    "descriptionLength": {
      "min": 5,
      "max": 200
    }
  }
}
```

## Testing

### Run Test Script

```bash
chmod +x test-configmap.sh
./test-configmap.sh
```

### Manual Testing

```bash
# 1. Create ConfigMap
kubectl apply -f configmap.yaml

# 2. Deploy Job
kubectl apply -f job.yaml

# 3. Wait for completion
kubectl wait --for=condition=complete --timeout=60s job/git-workflow-enforcer-job

# 4. Check logs
kubectl logs -l app=git-workflow-enforcer

# 5. Verify ConfigMap mount
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD_NAME -- cat /app/src/config/rules.json
```

## Monitoring

### Check Status

```bash
# Jobs
kubectl get jobs

# Deployments
kubectl get deployments

# CronJobs
kubectl get cronjobs

# Pods
kubectl get pods -l app=git-workflow-enforcer

# ConfigMaps
kubectl get configmap git-enforcer-config
```

### View Logs

```bash
# All pods
kubectl logs -l app=git-workflow-enforcer

# Specific pod
kubectl logs <pod-name>

# Follow logs
kubectl logs -f -l app=git-workflow-enforcer

# Previous logs (if pod restarted)
kubectl logs <pod-name> --previous
```

### Describe Resources

```bash
kubectl describe job git-workflow-enforcer-job
kubectl describe deployment git-workflow-enforcer
kubectl describe cronjob git-workflow-enforcer-cron
kubectl describe configmap git-enforcer-config
```

## Troubleshooting

### ConfigMap Not Found

```bash
# Check if exists
kubectl get configmap git-enforcer-config

# Create if missing
kubectl apply -f configmap.yaml
```

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -l app=git-workflow-enforcer

# View pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Invalid Configuration

```bash
# Validate JSON
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq .

# Fix and reapply
kubectl apply -f configmap.yaml
```

### Image Pull Issues

```bash
# Check image exists locally
docker images git-workflow-enforcer

# Build if missing
docker build -t git-workflow-enforcer:test ../../

# Verify imagePullPolicy
kubectl get job git-workflow-enforcer-job -o yaml | grep imagePullPolicy
```

## Cleanup

### Delete Specific Resources

```bash
kubectl delete -f job.yaml
kubectl delete -f deployment.yaml
kubectl delete -f cronjob.yaml
kubectl delete -f configmap.yaml
```

### Delete All

```bash
kubectl delete -f .
```

### Delete by Label

```bash
kubectl delete all -l app=git-workflow-enforcer
kubectl delete configmap -l app=git-workflow-enforcer
```

## Best Practices

### 1. Version Control

Keep all manifests in version control:
```bash
git add infrastructure/kubernetes/
git commit -m "feat: add kubernetes manifests with configmap"
```

### 2. Backup ConfigMap

Before making changes:
```bash
kubectl get configmap git-enforcer-config -o yaml > configmap-backup.yaml
```

### 3. Use Namespaces

Isolate resources:
```bash
kubectl create namespace git-enforcer
kubectl apply -f . -n git-enforcer
```

### 4. Label Resources

Add meaningful labels:
```yaml
metadata:
  labels:
    app: git-workflow-enforcer
    version: "1.0"
    environment: production
```

### 5. Document Changes

Use annotations:
```yaml
metadata:
  annotations:
    change-date: "2026-03-03"
    changed-by: "admin"
```

## Security

### Features Implemented

- ✅ Non-root user (UID 1000)
- ✅ Read-only root filesystem option
- ✅ No privilege escalation
- ✅ Capabilities dropped (ALL)
- ✅ Security contexts defined
- ✅ Resource limits enforced
- ✅ ConfigMap read-only mount

### Recommendations

- Use Pod Security Policies
- Enable Network Policies
- Implement RBAC
- Use Secrets for sensitive data
- Regular security audits

## Advanced Usage

### Multiple Environments

```bash
# Development
kubectl create configmap git-enforcer-config-dev --from-file=rules-dev.json -n development

# Production
kubectl create configmap git-enforcer-config-prod --from-file=rules-prod.json -n production
```

### Immutable ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: git-enforcer-config
immutable: true
data:
  rules.json: |
    {...}
```

### ConfigMap from Multiple Files

```bash
kubectl create configmap git-enforcer-config \
  --from-file=rules.json \
  --from-file=additional-config.json
```

## Integration

### CI/CD Pipeline

```yaml
# GitLab CI
deploy:
  script:
    - kubectl apply -f infrastructure/kubernetes/configmap.yaml
    - kubectl apply -f infrastructure/kubernetes/job.yaml
```

### Helm Chart (Future)

Consider creating a Helm chart for easier deployment:
```
git-workflow-enforcer/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── configmap.yaml
    ├── job.yaml
    └── deployment.yaml
```

## Documentation

- **CONFIGMAP-GUIDE.md** - Detailed ConfigMap usage
- **README.md** - This file
- **test-configmap.sh** - Test script

## Support

For issues or questions:
- GitHub Issues: https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer/issues
- Documentation: See main README.md

## Summary

✅ **ConfigMap Benefits**:
- No Docker image rebuild
- Easy rule updates
- Environment-specific configs
- Kubernetes-native solution

✅ **Key Features**:
- Externalized configuration
- Multiple deployment options
- Production-ready security
- Comprehensive documentation

✅ **Next Steps**:
1. Create ConfigMap
2. Deploy workload (Job/Deployment/CronJob)
3. Verify configuration
4. Update rules as needed

---

**Status**: Production Ready ✅  
**Last Updated**: March 3, 2026
