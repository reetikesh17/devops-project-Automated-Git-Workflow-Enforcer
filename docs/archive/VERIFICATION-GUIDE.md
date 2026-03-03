# ConfigMap Verification Guide

## Overview

This guide shows you how to verify that the ConfigMap is properly mounted and accessible in your Kubernetes pods.

## Problem: Cannot Exec into Completed Job Pods

When you try to exec into a Job pod that has completed:

```bash
kubectl exec -it git-workflow-enforcer-job-xxxxx -- ls /app/src/config
# Error: cannot exec into a container in a completed pod; current phase is Succeeded
```

This is expected behavior - Jobs complete and exit, so you can't exec into them after completion.

## Solution: Use Debug Deployment

### Method 1: Debug Deployment (Recommended)

We've created a debug deployment that stays running for verification.

#### 1. Deploy Debug Container

```bash
kubectl apply -f debug-deployment.yaml
```

#### 2. Wait for Pod to be Ready

```bash
kubectl get pods -l component=debug
```

Expected output:
```
NAME                                  READY   STATUS    RESTARTS   AGE
git-enforcer-debug-xxxxx              1/1     Running   0          10s
```

#### 3. Check Logs

```bash
kubectl logs -l component=debug
```

Expected output:
```
Debug container started
ConfigMap should be mounted at /app/src/config
Listing mounted config:
total 12
drwxrwxrwx 3 root     root     4096 Mar  3 12:45 .
drwxr-xr-x 9 enforcer enforcer 4096 Mar  1 12:00 ..
drwxr-xr-x 2 root     root     4096 Mar  3 12:45 ..2026_03_03_12_45_35.2232873928
lrwxrwxrwx 1 root     root       32 Mar  3 12:45 ..data -> ..2026_03_03_12_45_35.2232873928
lrwxrwxrwx 1 root     root       17 Mar  3 12:45 rules.json -> ..data/rules.json
```

#### 4. Exec into Pod

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l component=debug -o jsonpath='{.items[0].metadata.name}')

# Exec into pod
kubectl exec -it $POD_NAME -- /bin/sh
```

#### 5. Verify ConfigMap Content

Inside the pod:

```bash
# List config directory
ls -la /app/src/config/

# View rules.json
cat /app/src/config/rules.json

# Verify JSON is valid
cat /app/src/config/rules.json | python -m json.tool

# Check file permissions
ls -l /app/src/config/rules.json
```

#### 6. Test Validation with Mounted Config

```bash
# Inside the pod
cd /app
python -m src.main.cli validate-commit "feat: test with mounted config"
```

#### 7. Cleanup

```bash
kubectl delete -f debug-deployment.yaml
```

### Method 2: Check Job Pod Before Completion

If you want to check a Job pod, you need to do it quickly before it completes:

```bash
# Deploy job
kubectl apply -f job.yaml

# Immediately get pod name
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

# Quickly exec (within seconds)
kubectl exec -it $POD_NAME -- ls /app/src/config/
```

### Method 3: Check Pod Spec (Without Exec)

You can verify the volume configuration without exec:

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')

# Check volumes
kubectl get pod $POD_NAME -o jsonpath='{.spec.volumes}' | jq .

# Check volume mounts
kubectl get pod $POD_NAME -o jsonpath='{.spec.containers[0].volumeMounts}' | jq .

# Full pod spec
kubectl get pod $POD_NAME -o yaml
```

### Method 4: Use Deployment Instead of Job

For easier debugging, use a Deployment:

```bash
# Deploy
kubectl apply -f deployment.yaml

# Get pod name
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')

# Exec into running pod
kubectl exec -it $POD_NAME -- /bin/sh

# Inside pod
ls -la /app/src/config/
cat /app/src/config/rules.json
```

## Verification Checklist

### ✅ ConfigMap Exists

```bash
kubectl get configmap git-enforcer-config
```

Expected:
```
NAME                  DATA   AGE
git-enforcer-config   1      5m
```

### ✅ ConfigMap Contains rules.json

```bash
kubectl describe configmap git-enforcer-config
```

Should show `rules.json` in the Data section.

### ✅ ConfigMap Content is Valid JSON

```bash
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq .
```

Should parse without errors.

### ✅ Pod Has Volume Configured

```bash
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')
kubectl get pod $POD_NAME -o jsonpath='{.spec.volumes}' | jq '.[] | select(.name=="config-volume")'
```

Expected:
```json
{
  "configMap": {
    "defaultMode": 420,
    "items": [
      {
        "key": "rules.json",
        "path": "rules.json"
      }
    ],
    "name": "git-enforcer-config"
  },
  "name": "config-volume"
}
```

### ✅ Pod Has Volume Mount Configured

```bash
kubectl get pod $POD_NAME -o jsonpath='{.spec.containers[0].volumeMounts}' | jq '.[] | select(.name=="config-volume")'
```

Expected:
```json
{
  "mountPath": "/app/src/config",
  "name": "config-volume",
  "readOnly": true
}
```

### ✅ File Exists in Pod

Using debug deployment:

```bash
POD_NAME=$(kubectl get pods -l component=debug -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD_NAME -- ls -la /app/src/config/rules.json
```

Expected:
```
lrwxrwxrwx 1 root root 17 Mar  3 12:45 /app/src/config/rules.json -> ..data/rules.json
```

### ✅ File Content is Correct

```bash
kubectl exec $POD_NAME -- cat /app/src/config/rules.json
```

Should show the complete rules.json content.

### ✅ Application Can Read File

```bash
kubectl exec $POD_NAME -- python -c "import json; print(json.load(open('/app/src/config/rules.json')))"
```

Should parse and print the JSON.

## Common Issues and Solutions

### Issue 1: "cannot exec into a container in a completed pod"

**Cause**: Job has completed and exited.

**Solution**: Use debug deployment or deployment instead of job for testing.

```bash
kubectl apply -f debug-deployment.yaml
```

### Issue 2: ConfigMap Not Found

**Cause**: ConfigMap not created.

**Solution**: Create ConfigMap first.

```bash
kubectl apply -f configmap.yaml
```

### Issue 3: Volume Not Mounted

**Cause**: Volume configuration missing or incorrect.

**Solution**: Verify volume and volumeMount in pod spec.

```bash
kubectl get pod $POD_NAME -o yaml | grep -A 10 volumes:
kubectl get pod $POD_NAME -o yaml | grep -A 10 volumeMounts:
```

### Issue 4: File Not Found in Pod

**Cause**: Incorrect mount path or ConfigMap key.

**Solution**: Check mount path and ConfigMap items.

```yaml
volumeMounts:
- name: config-volume
  mountPath: /app/src/config  # Correct path

volumes:
- name: config-volume
  configMap:
    name: git-enforcer-config
    items:
    - key: rules.json  # Must match ConfigMap key
      path: rules.json  # File name in mount path
```

### Issue 5: Permission Denied

**Cause**: File permissions or security context.

**Solution**: Check file permissions and security context.

```bash
kubectl exec $POD_NAME -- ls -l /app/src/config/rules.json
```

ConfigMaps are mounted as read-only by default, which is correct.

## Quick Verification Script

Save this as `verify-configmap.sh`:

```bash
#!/bin/bash

echo "=== ConfigMap Verification ==="
echo ""

# 1. Check ConfigMap exists
echo "[1/6] Checking ConfigMap..."
kubectl get configmap git-enforcer-config || exit 1
echo "✓ ConfigMap exists"
echo ""

# 2. Validate JSON
echo "[2/6] Validating JSON..."
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq . > /dev/null || exit 1
echo "✓ JSON is valid"
echo ""

# 3. Deploy debug pod
echo "[3/6] Deploying debug pod..."
kubectl apply -f debug-deployment.yaml
sleep 10
echo "✓ Debug pod deployed"
echo ""

# 4. Check pod is running
echo "[4/6] Checking pod status..."
kubectl wait --for=condition=ready pod -l component=debug --timeout=60s || exit 1
echo "✓ Pod is running"
echo ""

# 5. Verify file exists
echo "[5/6] Verifying file exists..."
POD_NAME=$(kubectl get pods -l component=debug -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD_NAME -- ls /app/src/config/rules.json || exit 1
echo "✓ File exists"
echo ""

# 6. Verify content
echo "[6/6] Verifying content..."
kubectl exec $POD_NAME -- cat /app/src/config/rules.json | jq . > /dev/null || exit 1
echo "✓ Content is valid"
echo ""

echo "=== All Checks Passed! ==="
echo ""
echo "To exec into pod:"
echo "  kubectl exec -it $POD_NAME -- /bin/sh"
echo ""
echo "To cleanup:"
echo "  kubectl delete -f debug-deployment.yaml"
```

Run it:

```bash
chmod +x verify-configmap.sh
./verify-configmap.sh
```

## Interactive Debugging Session

### Start Debug Session

```bash
# Deploy debug pod
kubectl apply -f debug-deployment.yaml

# Wait for ready
kubectl wait --for=condition=ready pod -l component=debug --timeout=60s

# Get pod name
POD_NAME=$(kubectl get pods -l component=debug -o jsonpath='{.items[0].metadata.name}')

# Exec into pod
kubectl exec -it $POD_NAME -- /bin/sh
```

### Inside the Pod

```bash
# Navigate to app directory
cd /app

# Check config directory
ls -la src/config/

# View rules
cat src/config/rules.json

# Validate JSON
python -c "import json; json.load(open('src/config/rules.json'))"

# Test validation
python -m src.main.cli validate-commit "feat: test message"
python -m src.main.cli validate-branch "feature/TEST-123-test"

# Check Python can import config
python -c "from src.config import ConfigLoader; print('Config loaded successfully')"

# Exit
exit
```

### Cleanup

```bash
kubectl delete -f debug-deployment.yaml
```

## Summary

### For Jobs (Completed Pods)
- ❌ Cannot exec after completion
- ✅ Check logs: `kubectl logs <pod-name>`
- ✅ Check pod spec: `kubectl get pod <pod-name> -o yaml`

### For Debugging
- ✅ Use debug deployment (stays running)
- ✅ Exec into debug pod
- ✅ Verify file exists and content is correct

### For Production
- ✅ Use Deployment for long-running services
- ✅ Use Job for one-time tasks
- ✅ Use CronJob for scheduled tasks

---

**Key Takeaway**: Jobs complete and exit, so use a debug deployment or regular deployment for interactive debugging and verification.
