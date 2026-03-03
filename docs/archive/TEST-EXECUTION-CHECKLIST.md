# Test Execution Checklist

## Automated Git Workflow Enforcer - Complete Testing Guide

**Date**: March 3, 2026  
**Version**: 1.0

---

## Pre-Test Setup

### Environment Verification

```bash
# Check Docker
docker --version
docker ps

# Check Kubernetes
kubectl version --client
kubectl cluster-info

# Check Terraform
terraform --version

# Check AWS CLI (if testing Terraform)
aws --version
aws sts get-caller-identity
```

**Expected**:
- ✅ Docker running
- ✅ Kubernetes cluster accessible
- ✅ Terraform installed
- ✅ AWS credentials configured (optional)

---

## Test Execution Order

### Phase 1: Docker Tests (15 minutes)

#### Test 1.1: Build Image
```bash
cd /path/to/project
docker build -t git-workflow-enforcer:test .
```
**Expected**: Build completes successfully  
**Status**: [ ] PASS [ ] FAIL

#### Test 1.2: Run Container - Valid Input
```bash
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-commit "feat: test docker"
```
**Expected**: Exit code 0, success message  
**Status**: [ ] PASS [ ] FAIL

#### Test 1.3: Run Container - Invalid Input
```bash
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-commit "bad"
```
**Expected**: Exit code 1, error message  
**Status**: [ ] PASS [ ] FAIL

#### Test 1.4: CLI Help
```bash
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli --help
```
**Expected**: Help text displayed  
**Status**: [ ] PASS [ ] FAIL

---

### Phase 2: Kubernetes Tests (20 minutes)

#### Test 2.1: Apply ConfigMap
```bash
kubectl apply -f infrastructure/kubernetes/configmap.yaml
kubectl get configmap git-enforcer-config
```
**Expected**: ConfigMap created  
**Status**: [ ] PASS [ ] FAIL

#### Test 2.2: Validate ConfigMap Content
```bash
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq .
```
**Expected**: Valid JSON output  
**Status**: [ ] PASS [ ] FAIL

#### Test 2.3: Deploy Job
```bash
kubectl apply -f infrastructure/kubernetes/job.yaml
kubectl get jobs
```
**Expected**: Job created  
**Status**: [ ] PASS [ ] FAIL

#### Test 2.4: Wait for Job Completion
```bash
kubectl wait --for=condition=complete --timeout=60s job/git-workflow-enforcer-job
```
**Expected**: Job completes within 60s  
**Status**: [ ] PASS [ ] FAIL

#### Test 2.5: Check Pod Status
```bash
kubectl get pods -l app=git-workflow-enforcer
```
**Expected**: Pod status: Completed  
**Status**: [ ] PASS [ ] FAIL

#### Test 2.6: Inspect Logs
```bash
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME
```
**Expected**: Validation success message in logs  
**Status**: [ ] PASS [ ] FAIL

#### Test 2.7: Verify ConfigMap Mount
```bash
kubectl apply -f infrastructure/kubernetes/debug-deployment.yaml
kubectl wait --for=condition=ready pod -l component=debug --timeout=60s
DEBUG_POD=$(kubectl get pods -l component=debug -o jsonpath='{.items[0].metadata.name}')
kubectl exec $DEBUG_POD -- cat /app/src/config/rules.json
```
**Expected**: rules.json content displayed  
**Status**: [ ] PASS [ ] FAIL

#### Test 2.8: Test Failure Scenario
```bash
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: git-enforcer-fail-test
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: enforcer
        image: git-workflow-enforcer:test
        imagePullPolicy: Never
        command: ["python", "-m", "src.main.cli", "validate-commit", "bad"]
EOF

sleep 10
kubectl get job git-enforcer-fail-test
kubectl delete job git-enforcer-fail-test
```
**Expected**: Job fails as expected  
**Status**: [ ] PASS [ ] FAIL

---

### Phase 3: Scaling Tests (10 minutes)

#### Test 3.1: Deploy Scalable Deployment
```bash
kubectl apply -f infrastructure/kubernetes/deployment.yaml
kubectl get deployment git-workflow-enforcer
```
**Expected**: Deployment created, 1/1 ready  
**Status**: [ ] PASS [ ] FAIL

#### Test 3.2: Scale to 3 Replicas
```bash
kubectl scale deployment git-workflow-enforcer --replicas=3
kubectl wait --for=condition=available --timeout=60s deployment/git-workflow-enforcer
kubectl get pods -l app=git-workflow-enforcer
```
**Expected**: 3 pods running  
**Status**: [ ] PASS [ ] FAIL

#### Test 3.3: Verify Independent Execution
```bash
PODS=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[*].metadata.name}')
for POD in $PODS; do
  echo "=== $POD ==="
  kubectl logs $POD --tail=5
done
```
**Expected**: Each pod shows independent logs  
**Status**: [ ] PASS [ ] FAIL

#### Test 3.4: Scale Down
```bash
kubectl scale deployment git-workflow-enforcer --replicas=1
kubectl get deployment git-workflow-enforcer
```
**Expected**: Scaled down to 1/1  
**Status**: [ ] PASS [ ] FAIL

---

### Phase 4: Logging Tests (10 minutes)

#### Test 4.1: Basic Log Retrieval
```bash
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME
```
**Expected**: Logs displayed  
**Status**: [ ] PASS [ ] FAIL

#### Test 4.2: Logs with Timestamps
```bash
kubectl logs $POD_NAME --timestamps
```
**Expected**: Logs with timestamps  
**Status**: [ ] PASS [ ] FAIL

#### Test 4.3: Validation Output in Logs
```bash
kubectl logs $POD_NAME | grep "✓"
```
**Expected**: Success message found  
**Status**: [ ] PASS [ ] FAIL

#### Test 4.4: Error Handling Logs
```bash
# Already tested in Test 2.8
```
**Expected**: Error messages properly logged  
**Status**: [ ] PASS [ ] FAIL

---

### Phase 5: Terraform Tests (30 minutes)

**Note**: Requires AWS credentials

#### Test 5.1: Initialize Terraform
```bash
cd infrastructure/terraform
terraform init
```
**Expected**: Initialization successful  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

#### Test 5.2: Validate Configuration
```bash
terraform validate
```
**Expected**: Validation passes  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

#### Test 5.3: Format Check
```bash
terraform fmt -check -recursive
```
**Expected**: No formatting issues  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

#### Test 5.4: Create Test Variables
```bash
cat > test.tfvars <<EOF
aws_region    = "ap-south-1"
instance_type = "t2.micro"
environment   = "Dev"
key_name      = "test-key"
my_ip         = "203.0.113.0/32"
project_name  = "git-workflow-enforcer"
EOF
```
**Expected**: File created  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

#### Test 5.5: Run Plan
```bash
terraform plan -var-file=test.tfvars
```
**Expected**: Plan shows 2 resources to add  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

#### Test 5.6: Apply (Optional - Creates Real Resources)
```bash
# Only run if you want to create actual AWS resources
terraform apply -var-file=test.tfvars -auto-approve
```
**Expected**: Resources created successfully  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

#### Test 5.7: Verify Instance State (If Applied)
```bash
INSTANCE_ID=$(terraform output -raw instance_id)
aws ec2 describe-instances --instance-ids $INSTANCE_ID
```
**Expected**: Instance running  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

#### Test 5.8: Verify Security Group (If Applied)
```bash
SG_ID=$(terraform output -raw security_group_id)
aws ec2 describe-security-groups --group-ids $SG_ID
```
**Expected**: Security group configured correctly  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

#### Test 5.9: Destroy (If Applied)
```bash
terraform destroy -var-file=test.tfvars -auto-approve
```
**Expected**: All resources destroyed  
**Status**: [ ] PASS [ ] FAIL [ ] SKIP

---

## Cleanup

### Kubernetes Cleanup
```bash
kubectl delete -f infrastructure/kubernetes/debug-deployment.yaml
kubectl delete -f infrastructure/kubernetes/deployment.yaml
kubectl delete -f infrastructure/kubernetes/job.yaml
kubectl delete -f infrastructure/kubernetes/configmap.yaml
```

### Docker Cleanup
```bash
docker rmi git-workflow-enforcer:test
docker system prune -f
```

---

## Test Summary

### Results

| Phase | Tests | Passed | Failed | Skipped |
|-------|-------|--------|--------|---------|
| Docker | 4 | [ ] | [ ] | [ ] |
| Kubernetes | 8 | [ ] | [ ] | [ ] |
| Scaling | 4 | [ ] | [ ] | [ ] |
| Logging | 4 | [ ] | [ ] | [ ] |
| Terraform | 9 | [ ] | [ ] | [ ] |
| **Total** | **29** | **[ ]** | **[ ]** | **[ ]** |

### Overall Status

- [ ] All tests passed
- [ ] Some tests failed (see details above)
- [ ] Some tests skipped (Terraform requires AWS)

### Sign-off

**Tested By**: ___________________  
**Date**: ___________________  
**Signature**: ___________________

---

## Troubleshooting

### Common Issues

1. **Docker build fails**
   - Check Dockerfile syntax
   - Verify requirements.txt exists
   - Check network connectivity

2. **Kubernetes pod not starting**
   - Check image pull policy
   - Verify ConfigMap exists
   - Check resource limits

3. **ConfigMap not mounted**
   - Verify volume configuration
   - Check mount path
   - Verify ConfigMap name

4. **Terraform plan fails**
   - Check AWS credentials
   - Verify region availability
   - Check variable values

---

## Next Steps

After all tests pass:

1. **Documentation Review**
   - Update README.md
   - Review architecture docs
   - Update deployment guides

2. **Production Deployment**
   - Deploy to production environment
   - Configure monitoring
   - Set up alerts

3. **Team Training**
   - Train team on usage
   - Document procedures
   - Create runbooks

4. **Continuous Improvement**
   - Gather feedback
   - Implement enhancements
   - Regular reviews

---

**Test Plan Version**: 1.0  
**Last Updated**: March 3, 2026  
**Status**: Ready for Execution
