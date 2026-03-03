# ConfigMap Guide - Git Workflow Enforcer

## Overview

This guide explains how to use Kubernetes ConfigMaps to externalize validation rules for the Git Workflow Enforcer, allowing you to modify rules without rebuilding the Docker image.

## Architecture

```
┌─────────────────────────────────────────┐
│         ConfigMap                       │
│  (git-enforcer-config)                  │
│                                         │
│  Contains: rules.json                   │
│  - Branch patterns                      │
│  - Commit types                         │
│  - Validation rules                     │
└─────────────────────────────────────────┘
                  │
                  │ Mounted as Volume
                  ↓
┌─────────────────────────────────────────┐
│         Pod (Job/Deployment)            │
│                                         │
│  Volume Mount:                          │
│  /app/src/config/rules.json             │
│                                         │
│  Application reads rules from           │
│  mounted ConfigMap                      │
└─────────────────────────────────────────┘
```

## Files

1. **configmap.yaml** - ConfigMap definition with rules.json
2. **job.yaml** - Job with ConfigMap mounted
3. **deployment.yaml** - Deployment with ConfigMap mounted
4. **cronjob.yaml** - CronJob with ConfigMap mounted

## Quick Start

### 1. Create ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 2. Verify ConfigMap

```bash
# View ConfigMap
kubectl get configmap git-enforcer-config

# View ConfigMap details
kubectl describe configmap git-enforcer-config

# View rules.json content
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq .
```

### 3. Deploy Job with ConfigMap

```bash
kubectl apply -f job.yaml
```

### 4. Verify Job Uses ConfigMap

```bash
# Check job status
kubectl get jobs

# View pod logs
kubectl logs -l app=git-workflow-enforcer

# Verify mounted config
kubectl exec -it <pod-name> -- cat /app/src/config/rules.json
```

## ConfigMap Structure

### rules.json Schema

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
  },
  "validation": {
    "strictMode": false,
    "blockOnWarning": false,
    "validateOnCommit": true,
    "validateOnPush": true
  }
}
```

## Modifying Rules

### Method 1: Edit ConfigMap Directly

```bash
kubectl edit configmap git-enforcer-config
```

This opens the ConfigMap in your default editor. Make changes and save.

### Method 2: Update from File

```bash
# Edit configmap.yaml
nano configmap.yaml

# Apply changes
kubectl apply -f configmap.yaml
```

### Method 3: Patch ConfigMap

```bash
kubectl patch configmap git-enforcer-config --patch '
data:
  rules.json: |
    {
      "version": "1.0",
      "branches": {
        "patterns": {
          "feature": "^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$"
        }
      }
    }
'
```

### Method 4: Replace from JSON File

```bash
# Create new rules.json
cat > new-rules.json << 'EOF'
{
  "version": "1.0",
  "branches": {
    "patterns": {
      "feature": "^feature/PROJ-[0-9]+-[a-z0-9-]+$"
    }
  }
}
EOF

# Delete old ConfigMap
kubectl delete configmap git-enforcer-config

# Create new ConfigMap from file
kubectl create configmap git-enforcer-config --from-file=rules.json=new-rules.json
```

## Reloading Configuration

### For Jobs

Jobs are immutable. To use updated ConfigMap:

```bash
# Delete old job
kubectl delete job git-workflow-enforcer-job

# Create new job (will use updated ConfigMap)
kubectl apply -f job.yaml
```

### For Deployments

Deployments need to be restarted to pick up ConfigMap changes:

```bash
# Method 1: Rollout restart
kubectl rollout restart deployment git-workflow-enforcer

# Method 2: Delete pods (they will be recreated)
kubectl delete pods -l app=git-workflow-enforcer

# Method 3: Scale down and up
kubectl scale deployment git-workflow-enforcer --replicas=0
kubectl scale deployment git-workflow-enforcer --replicas=1
```

### For CronJobs

CronJobs will use the updated ConfigMap on the next scheduled run. To test immediately:

```bash
# Create a manual job from cronjob
kubectl create job --from=cronjob/git-workflow-enforcer-cron manual-test
```

## Example Configurations

### Strict Mode Configuration

```json
{
  "version": "1.0",
  "branches": {
    "patterns": {
      "feature": "^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$",
      "bugfix": "^bugfix/[A-Z]+-[0-9]+-[a-z0-9-]+$"
    },
    "protected": ["main", "master", "develop", "staging"],
    "ticketIdPattern": "[A-Z]+-[0-9]+"
  },
  "commits": {
    "types": ["feat", "fix"],
    "descriptionLength": {
      "min": 20,
      "max": 72
    },
    "enforceCase": "lowercase",
    "allowBreakingChanges": false
  },
  "validation": {
    "strictMode": true,
    "blockOnWarning": true,
    "validateOnCommit": true,
    "validateOnPush": true
  }
}
```

### Relaxed Mode Configuration

```json
{
  "version": "1.0",
  "branches": {
    "patterns": {
      "feature": "^feature/.*$",
      "bugfix": "^bugfix/.*$",
      "hotfix": "^hotfix/.*$"
    },
    "protected": ["main"],
    "ticketIdPattern": ".*"
  },
  "commits": {
    "types": ["feat", "fix", "chore", "docs", "refactor", "test", "ci", "style", "perf"],
    "descriptionLength": {
      "min": 5,
      "max": 200
    },
    "enforceCase": "any",
    "allowBreakingChanges": true
  },
  "validation": {
    "strictMode": false,
    "blockOnWarning": false,
    "validateOnCommit": false,
    "validateOnPush": true
  }
}
```

### Custom Project Configuration

```json
{
  "version": "1.0",
  "branches": {
    "patterns": {
      "feature": "^feature/PROJ-[0-9]+-[a-z0-9-]+$",
      "bugfix": "^bugfix/PROJ-[0-9]+-[a-z0-9-]+$",
      "hotfix": "^hotfix/PROJ-[0-9]+$",
      "release": "^release/v[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "protected": ["main", "production", "staging"],
    "ticketIdPattern": "PROJ-[0-9]+"
  },
  "commits": {
    "types": ["feat", "fix", "docs", "chore"],
    "descriptionLength": {
      "min": 15,
      "max": 80
    },
    "enforceCase": "lowercase",
    "allowBreakingChanges": true
  },
  "validation": {
    "strictMode": false,
    "blockOnWarning": false,
    "validateOnCommit": true,
    "validateOnPush": true
  }
}
```

## Testing Configuration Changes

### 1. Create Test ConfigMap

```bash
kubectl create configmap git-enforcer-config-test --from-file=rules.json=test-rules.json
```

### 2. Create Test Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: git-workflow-enforcer-test
spec:
  template:
    spec:
      containers:
      - name: enforcer
        image: git-workflow-enforcer:test
        command: ["python", "-m", "src.main.cli", "validate-commit", "feat: test"]
        volumeMounts:
        - name: config-volume
          mountPath: /app/src/config
      volumes:
      - name: config-volume
        configMap:
          name: git-enforcer-config-test
      restartPolicy: Never
```

### 3. Run Test

```bash
kubectl apply -f test-job.yaml
kubectl logs -l job-name=git-workflow-enforcer-test
```

### 4. Cleanup

```bash
kubectl delete job git-workflow-enforcer-test
kubectl delete configmap git-enforcer-config-test
```

## Troubleshooting

### ConfigMap Not Found

```bash
# Check if ConfigMap exists
kubectl get configmap git-enforcer-config

# If not, create it
kubectl apply -f configmap.yaml
```

### Pod Not Using Updated ConfigMap

```bash
# Check pod creation time
kubectl get pods -l app=git-workflow-enforcer -o wide

# Check ConfigMap update time
kubectl get configmap git-enforcer-config -o yaml | grep creationTimestamp

# Restart pods
kubectl rollout restart deployment git-workflow-enforcer
```

### Invalid JSON in ConfigMap

```bash
# Validate JSON
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq .

# If invalid, fix and reapply
kubectl apply -f configmap.yaml
```

### Rules Not Being Applied

```bash
# Check if volume is mounted
kubectl describe pod <pod-name> | grep -A 5 "Mounts:"

# Check file exists in pod
kubectl exec -it <pod-name> -- ls -la /app/src/config/

# Check file content
kubectl exec -it <pod-name> -- cat /app/src/config/rules.json
```

## Best Practices

### 1. Version Control

Keep ConfigMap definitions in version control:

```bash
git add infrastructure/kubernetes/configmap.yaml
git commit -m "feat: update validation rules"
```

### 2. Backup Before Changes

```bash
kubectl get configmap git-enforcer-config -o yaml > configmap-backup.yaml
```

### 3. Use Namespaces

```bash
kubectl create namespace git-enforcer
kubectl apply -f configmap.yaml -n git-enforcer
kubectl apply -f job.yaml -n git-enforcer
```

### 4. Label ConfigMaps

```yaml
metadata:
  labels:
    app: git-workflow-enforcer
    version: "1.0"
    environment: production
```

### 5. Document Changes

Add annotations to track changes:

```yaml
metadata:
  annotations:
    change-date: "2026-03-03"
    changed-by: "admin"
    change-reason: "Updated branch patterns for new project"
```

## Advanced Usage

### Multiple Environments

```bash
# Development
kubectl create configmap git-enforcer-config-dev --from-file=rules-dev.json
kubectl apply -f job.yaml -n development

# Production
kubectl create configmap git-enforcer-config-prod --from-file=rules-prod.json
kubectl apply -f job.yaml -n production
```

### ConfigMap Immutability

For production, make ConfigMap immutable:

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

### Hot Reload (Advanced)

For applications that support hot reload, use a sidecar:

```yaml
containers:
- name: config-reloader
  image: jimmidyson/configmap-reload:latest
  args:
  - --volume-dir=/config
  - --webhook-url=http://localhost:8080/reload
  volumeMounts:
  - name: config-volume
    mountPath: /config
```

## Monitoring

### Watch ConfigMap Changes

```bash
kubectl get configmap git-enforcer-config --watch
```

### Audit ConfigMap Changes

```bash
kubectl get events --field-selector involvedObject.name=git-enforcer-config
```

### Check ConfigMap Usage

```bash
# Find pods using the ConfigMap
kubectl get pods -o json | jq '.items[] | select(.spec.volumes[]?.configMap.name=="git-enforcer-config") | .metadata.name'
```

## Summary

✅ **Benefits of ConfigMap Approach**:
- No Docker image rebuild required
- Easy rule updates
- Environment-specific configurations
- Version control friendly
- Kubernetes-native solution

✅ **Key Points**:
- ConfigMap mounted at `/app/src/config/rules.json`
- Pods must be restarted to pick up changes
- Jobs are immutable (delete and recreate)
- Always validate JSON before applying

✅ **Next Steps**:
1. Create ConfigMap: `kubectl apply -f configmap.yaml`
2. Deploy Job: `kubectl apply -f job.yaml`
3. Verify: `kubectl logs -l app=git-workflow-enforcer`
4. Modify rules as needed
5. Restart pods to apply changes

---

For more information, see the main Kubernetes documentation in the infrastructure/kubernetes/ directory.
