# Quick Reference - ConfigMap Verification

## ⚠️ Common Error

```bash
kubectl exec -it <job-pod-name> -- ls /app/src/config
# Error: cannot exec into a container in a completed pod; current phase is Succeeded
```

**Why?** Jobs complete and exit. You can't exec into completed pods.

## ✅ Solution: Use Debug Deployment

### Quick Commands

```bash
# 1. Deploy debug pod (stays running)
kubectl apply -f debug-deployment.yaml

# 2. Get pod name
POD=$(kubectl get pods -l component=debug -o jsonpath='{.items[0].metadata.name}')

# 3. Exec into pod
kubectl exec -it $POD -- /bin/sh

# 4. Inside pod - verify config
ls -la /app/src/config/
cat /app/src/config/rules.json

# 5. Cleanup
kubectl delete -f debug-deployment.yaml
```

## 📋 Verification Checklist

```bash
# ConfigMap exists
kubectl get configmap git-enforcer-config

# View ConfigMap content
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq .

# Check volume in pod
kubectl get pod $POD -o jsonpath='{.spec.volumes}' | jq .

# Check volume mount
kubectl get pod $POD -o jsonpath='{.spec.containers[0].volumeMounts}' | jq .

# View file in pod
kubectl exec $POD -- cat /app/src/config/rules.json
```

## 🔍 Debug vs Production

| Type | Use Case | Can Exec? | Command |
|------|----------|-----------|---------|
| **Job** | One-time task | ❌ After completion | `kubectl apply -f job.yaml` |
| **Deployment** | Long-running | ✅ Yes | `kubectl apply -f deployment.yaml` |
| **Debug** | Testing | ✅ Yes | `kubectl apply -f debug-deployment.yaml` |

## 🚀 Quick Test

```bash
# Full test in one command
kubectl apply -f debug-deployment.yaml && \
sleep 10 && \
POD=$(kubectl get pods -l component=debug -o jsonpath='{.items[0].metadata.name}') && \
kubectl exec $POD -- cat /app/src/config/rules.json | jq .
```

## 📝 Update ConfigMap

```bash
# Edit ConfigMap
kubectl edit configmap git-enforcer-config

# Restart pods to pick up changes
kubectl rollout restart deployment git-enforcer-debug

# Or delete and recreate job
kubectl delete job git-workflow-enforcer-job
kubectl apply -f job.yaml
```

## 🧹 Cleanup

```bash
# Delete debug deployment
kubectl delete -f debug-deployment.yaml

# Delete job
kubectl delete -f job.yaml

# Delete ConfigMap
kubectl delete -f configmap.yaml

# Delete all
kubectl delete -f .
```

---

**Remember**: Jobs complete and exit. Use debug deployment for interactive testing!
