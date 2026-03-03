# Final Infrastructure Testing and Documentation Plan

**Project**: Automated Git Workflow Enforcer  
**Date**: March 3, 2026  
**Version**: 1.0  
**Status**: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Docker Validation](#docker-validation)
3. [Kubernetes Validation](#kubernetes-validation)
4. [Scaling Tests](#scaling-tests)
5. [Logging Validation](#logging-validation)
6. [Terraform Infrastructure Validation](#terraform-infrastructure-validation)
7. [End-to-End Architecture](#end-to-end-architecture)
8. [Production Readiness Review](#production-readiness-review)
9. [Test Execution Checklist](#test-execution-checklist)
10. [Professional Documentation](#professional-documentation)

---

## Overview

This comprehensive testing plan validates the complete DevOps pipeline from local development to cloud infrastructure deployment.

### Testing Scope

- ✅ Docker containerization
- ✅ Kubernetes orchestration
- ✅ ConfigMap configuration management
- ✅ Terraform infrastructure provisioning
- ✅ CI/CD integration
- ✅ Production readiness

### Prerequisites

- Docker installed and running
- Kubernetes cluster available (Docker Desktop/Minikube)
- kubectl configured
- Terraform installed
- AWS credentials configured (for Terraform tests)
- Git repository cloned

---

## 1. Docker Validation

### 1.1 Build Image Test

**Objective**: Verify Docker image builds successfully

**Commands**:
```bash
# Build image
docker build -t git-workflow-enforcer:test .

# Verify image exists
docker images git-workflow-enforcer:test

# Check image size
docker images git-workflow-enforcer:test --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

**Expected Results**:
- ✅ Build completes without errors
- ✅ Image size < 400MB
- ✅ Image tagged correctly

**Success Criteria**:
```
REPOSITORY              TAG    SIZE
git-workflow-enforcer   test   327MB
```

---

### 1.2 Run Container Test

**Objective**: Verify container runs and executes commands

**Commands**:
```bash
# Test commit validation (valid)
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-commit "feat: test docker container"

# Test commit validation (invalid)
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-commit "invalid message"

# Test branch validation (valid)
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-branch "feature/TEST-123-docker-test"

# Test branch validation (invalid)
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-branch "invalid-branch"
```

**Expected Results**:
- ✅ Valid commit: Exit code 0, success message
- ✅ Invalid commit: Exit code 1, error message
- ✅ Valid branch: Exit code 0, success message
- ✅ Invalid branch: Exit code 1, error message

---

### 1.3 CLI Output Validation

**Objective**: Verify CLI produces correct output format

**Test Script**:
```bash
#!/bin/bash
echo "Testing CLI Output..."

# Test 1: Valid commit
OUTPUT=$(docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-commit "feat: test message" 2>&1)
echo "$OUTPUT" | grep -q "✓ Commit message is valid" && echo "✅ Test 1 PASS" || echo "❌ Test 1 FAIL"

# Test 2: Invalid commit
OUTPUT=$(docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-commit "bad" 2>&1)
echo "$OUTPUT" | grep -q "INVALID" && echo "✅ Test 2 PASS" || echo "❌ Test 2 FAIL"

# Test 3: Help command
OUTPUT=$(docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli --help 2>&1)
echo "$OUTPUT" | grep -q "usage:" && echo "✅ Test 3 PASS" || echo "❌ Test 3 FAIL"
```

---

### 1.4 Exit Code Validation

**Objective**: Confirm correct exit codes for success/failure

**Test Script**:
```bash
#!/bin/bash
echo "Testing Exit Codes..."

# Test valid commit (should return 0)
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-commit "feat: test"
if [ $? -eq 0 ]; then echo "✅ Valid commit: Exit 0"; else echo "❌ FAIL"; fi

# Test invalid commit (should return 1)
docker run --rm git-workflow-enforcer:test \
  python -m src.main.cli validate-commit "bad"
if [ $? -eq 1 ]; then echo "✅ Invalid commit: Exit 1"; else echo "❌ FAIL"; fi
```

**Expected Exit Codes**:
- `0` - Validation successful
- `1` - Validation failed
- `2` - Configuration error
- `3` - Runtime error

---

## 2. Kubernetes Validation

### 2.1 Apply ConfigMap

**Objective**: Verify ConfigMap creation and content

**Commands**:
```bash
# Apply ConfigMap
kubectl apply -f infrastructure/kubernetes/configmap.yaml

# Verify ConfigMap exists
kubectl get configmap git-enforcer-config

# Describe ConfigMap
kubectl describe configmap git-enforcer-config

# Validate JSON content
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq .
```

**Expected Results**:
- ✅ ConfigMap created successfully
- ✅ Contains rules.json key
- ✅ JSON is valid
- ✅ All validation rules present

**Success Output**:
```
NAME                  DATA   AGE
git-enforcer-config   1      10s
```

---

### 2.2 Deploy Job

**Objective**: Deploy and verify Kubernetes Job

**Commands**:
```bash
# Apply Job
kubectl apply -f infrastructure/kubernetes/job.yaml

# Check Job status
kubectl get jobs

# Wait for completion
kubectl wait --for=condition=complete --timeout=60s job/git-workflow-enforcer-job
```

**Expected Results**:
- ✅ Job created successfully
- ✅ Job completes within 60 seconds
- ✅ COMPLETIONS shows 1/1

**Success Output**:
```
NAME                        STATUS     COMPLETIONS   DURATION   AGE
git-workflow-enforcer-job   Complete   1/1           7s         15s
```

---

### 2.3 Verify Pod Status

**Objective**: Check Pod lifecycle and status

**Commands**:
```bash
# Get pods
kubectl get pods -l app=git-workflow-enforcer

# Describe pod
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $POD_NAME

# Check pod events
kubectl get events --field-selector involvedObject.name=$POD_NAME
```

**Expected Results**:
- ✅ Pod status: Completed
- ✅ No error events
- ✅ Container exit code: 0

---

### 2.4 Inspect Logs

**Objective**: Verify validation execution in logs

**Commands**:
```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')

# View logs
kubectl logs $POD_NAME

# Check for success message
kubectl logs $POD_NAME | grep "✓"
```

**Expected Log Output**:
```
INFO: Validating commit message...
✓ Commit message is valid
```

---

### 2.5 Confirm Mounted Configuration

**Objective**: Verify ConfigMap is properly mounted

**Commands**:
```bash
# Deploy debug pod
kubectl apply -f infrastructure/kubernetes/debug-deployment.yaml

# Wait for pod
kubectl wait --for=condition=ready pod -l component=debug --timeout=60s

# Get debug pod name
DEBUG_POD=$(kubectl get pods -l component=debug -o jsonpath='{.items[0].metadata.name}')

# Check mounted volume
kubectl exec $DEBUG_POD -- ls -la /app/src/config/

# View mounted config
kubectl exec $DEBUG_POD -- cat /app/src/config/rules.json

# Verify volume in pod spec
kubectl get pod $DEBUG_POD -o jsonpath='{.spec.volumes}' | jq '.[] | select(.name=="config-volume")'
```

**Expected Results**:
- ✅ rules.json file exists at /app/src/config/
- ✅ File is readable
- ✅ Content matches ConfigMap
- ✅ Volume properly configured

---

### 2.6 Test Failure Scenario

**Objective**: Verify Job handles failures correctly

**Create Failure Test**:
```bash
# Create job with invalid command
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
        command: ["python", "-m", "src.main.cli", "validate-commit", "invalid"]
EOF

# Wait and check status
sleep 10
kubectl get job git-enforcer-fail-test

# Check pod status
kubectl get pods -l job-name=git-enforcer-fail-test

# View logs
POD_NAME=$(kubectl get pods -l job-name=git-enforcer-fail-test -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME

# Cleanup
kubectl delete job git-enforcer-fail-test
```

**Expected Results**:
- ✅ Job shows as Failed or with 0/1 completions
- ✅ Pod exit code is non-zero
- ✅ Logs show validation error
- ✅ Backoff retry mechanism works

---

### 2.7 Validate Job Completion Status

**Objective**: Confirm Job completion and cleanup

**Commands**:
```bash
# Check job status
kubectl get job git-workflow-enforcer-job -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}'

# Check completion time
kubectl get job git-workflow-enforcer-job -o jsonpath='{.status.completionTime}'

# Verify TTL cleanup (wait 1 hour or check spec)
kubectl get job git-workflow-enforcer-job -o jsonpath='{.spec.ttlSecondsAfterFinished}'
```

**Expected Results**:
- ✅ Completion status: True
- ✅ Completion time recorded
- ✅ TTL set to 3600 seconds
- ✅ Job will auto-cleanup after 1 hour

---

## 3. Scaling Tests (Kubernetes)

### 3.1 Deploy Scalable Deployment

**Objective**: Test horizontal scaling capabilities

**Commands**:
```bash
# Apply Deployment
kubectl apply -f infrastructure/kubernetes/deployment.yaml

# Verify initial replica count
kubectl get deployment git-workflow-enforcer

# Check pods
kubectl get pods -l app=git-workflow-enforcer
```

**Expected Initial State**:
```
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
git-workflow-enforcer   1/1     1            1           10s
```

---

### 3.2 Scale Replicas

**Objective**: Scale deployment and verify multiple pods

**Commands**:
```bash
# Scale to 3 replicas
kubectl scale deployment git-workflow-enforcer --replicas=3

# Wait for all replicas
kubectl wait --for=condition=available --timeout=60s deployment/git-workflow-enforcer

# Verify replica count
kubectl get deployment git-workflow-enforcer

# List all pods
kubectl get pods -l app=git-workflow-enforcer -o wide
```

**Expected Results**:
- ✅ Deployment shows 3/3 ready
- ✅ 3 pods running
- ✅ All pods in Running state
- ✅ Pods distributed (if multi-node cluster)

**Success Output**:
```
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
git-workflow-enforcer   3/3     3            3           2m

NAME                                    READY   STATUS    RESTARTS   AGE
git-workflow-enforcer-xxxxx-aaaaa       1/1     Running   0          30s
git-workflow-enforcer-xxxxx-bbbbb       1/1     Running   0          30s
git-workflow-enforcer-xxxxx-ccccc       1/1     Running   0          30s
```

---

### 3.3 Validate Independent Execution

**Objective**: Confirm each pod executes independently

**Commands**:
```bash
# Get all pod names
PODS=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[*].metadata.name}')

# Check logs from each pod
for POD in $PODS; do
  echo "=== Logs from $POD ==="
  kubectl logs $POD --tail=10
  echo ""
done

# Verify each pod has unique identity
for POD in $PODS; do
  echo "Pod: $POD"
  kubectl exec $POD -- hostname
done
```

**Expected Results**:
- ✅ Each pod shows independent logs
- ✅ Each pod has unique hostname
- ✅ All pods execute validation
- ✅ No resource conflicts

---

### 3.4 Scale Down Test

**Objective**: Test graceful scale-down

**Commands**:
```bash
# Scale down to 1
kubectl scale deployment git-workflow-enforcer --replicas=1

# Watch termination
kubectl get pods -l app=git-workflow-enforcer --watch

# Verify final state
kubectl get deployment git-workflow-enforcer
```

**Expected Results**:
- ✅ Pods terminate gracefully
- ✅ Final state: 1/1 ready
- ✅ No errors during scale-down

---

## 4. Logging Validation

### 4.1 Basic Log Retrieval

**Objective**: Verify log accessibility and format

**Commands**:
```bash
# Get logs from Job
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME

# Get logs with timestamps
kubectl logs $POD_NAME --timestamps

# Get logs from all pods (if multiple)
kubectl logs -l app=git-workflow-enforcer --all-containers=true

# Follow logs in real-time
kubectl logs -f -l app=git-workflow-enforcer
```

**Expected Log Format**:
```
2026-03-03T12:00:00.000Z INFO: Validating commit message...
2026-03-03T12:00:00.100Z ✓ Commit message is valid
```

---

### 4.2 Validation Output Verification

**Objective**: Confirm validation messages in logs

**Test Cases**:
```bash
# Test 1: Successful validation
kubectl logs $POD_NAME | grep "✓ Commit message is valid"
if [ $? -eq 0 ]; then echo "✅ Success message found"; fi

# Test 2: Check for INFO level
kubectl logs $POD_NAME | grep "INFO:"
if [ $? -eq 0 ]; then echo "✅ INFO logs present"; fi

# Test 3: No ERROR messages (for successful run)
kubectl logs $POD_NAME | grep "ERROR:"
if [ $? -ne 0 ]; then echo "✅ No errors (as expected)"; fi
```

---

### 4.3 Error Handling Behavior

**Objective**: Verify error logging and handling

**Create Error Scenario**:
```bash
# Deploy job with invalid input
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: git-enforcer-error-test
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

# Wait for completion
sleep 10

# Get pod name
ERROR_POD=$(kubectl get pods -l job-name=git-enforcer-error-test -o jsonpath='{.items[0].metadata.name}')

# Check logs for error messages
kubectl logs $ERROR_POD

# Verify error indicators
kubectl logs $ERROR_POD | grep -E "(ERROR|INVALID|❌)"

# Check exit code
kubectl get pod $ERROR_POD -o jsonpath='{.status.containerStatuses[0].state.terminated.exitCode}'

# Cleanup
kubectl delete job git-enforcer-error-test
```

**Expected Error Log**:
```
INFO: Validating commit message...

======================================================================
❌ INVALID COMMIT MESSAGE
======================================================================

Your message:
  bad

Error: Description too short (minimum 10 characters)
```

---

### 4.4 Log Aggregation Test

**Objective**: Test log collection from multiple pods

**Commands**:
```bash
# Scale deployment
kubectl scale deployment git-workflow-enforcer --replicas=3

# Collect logs from all pods
kubectl logs -l app=git-workflow-enforcer --prefix=true --all-containers=true

# Export logs to file
kubectl logs -l app=git-workflow-enforcer --all-containers=true > all-pods-logs.txt

# Count log entries
kubectl logs -l app=git-workflow-enforcer --all-containers=true | wc -l
```

**Expected Results**:
- ✅ Logs from all pods collected
- ✅ Pod names prefixed in output
- ✅ Logs properly formatted
- ✅ No log loss

---

### 4.5 Previous Container Logs

**Objective**: Access logs from restarted containers

**Commands**:
```bash
# Get previous logs (if pod restarted)
kubectl logs $POD_NAME --previous

# Check restart count
kubectl get pod $POD_NAME -o jsonpath='{.status.containerStatuses[0].restartCount}'
```

**Note**: This test only applies if pods have restarted.

---

## 5. Terraform Infrastructure Validation

### 5.1 Terraform Plan Verification

**Objective**: Validate Terraform configuration without applying

**Commands**:
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format check
terraform fmt -check -recursive

# Create test variables
cat > test.tfvars <<EOF
aws_region    = "ap-south-1"
instance_type = "t2.micro"
environment   = "Dev"
key_name      = "test-key"
my_ip         = "203.0.113.0/32"
project_name  = "git-workflow-enforcer"
EOF

# Run plan (requires AWS credentials)
terraform plan -var-file=test.tfvars
```

**Expected Results**:
- ✅ Initialization successful
- ✅ Validation passes
- ✅ No formatting issues
- ✅ Plan shows resources to create:
  - 1 Security Group
  - 1 EC2 Instance
  - 2 Data sources (VPC, AMI)

**Success Output**:
```
Plan: 2 to add, 0 to change, 0 to destroy.
```

---

### 5.2 Terraform Apply Confirmation

**Objective**: Deploy infrastructure (if AWS credentials available)

**Commands**:
```bash
# Apply configuration
terraform apply -var-file=test.tfvars -auto-approve

# Wait for completion
# (typically 2-3 minutes)

# Verify state
terraform show

# List resources
terraform state list
```

**Expected Resources Created**:
```
aws_instance.git_workflow_enforcer
aws_security_group.git_workflow_enforcer
data.aws_ami.amazon_linux_2
data.aws_vpc.default
```

---

### 5.3 Validate EC2 Instance State

**Objective**: Confirm EC2 instance is running

**Commands**:
```bash
# Get instance ID
INSTANCE_ID=$(terraform output -raw instance_id)

# Check instance state via AWS CLI
aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].State.Name' \
  --output text

# Check instance details
aws ec2 describe-instances --instance-ids $INSTANCE_ID

# Verify tags
aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].Tags'
```

**Expected Results**:
- ✅ Instance state: running
- ✅ Instance type: t2.micro
- ✅ Tags present:
  - Name: git-workflow-enforcer
  - Project: GitWorkflowEnforcer
  - Environment: Dev

---

### 5.4 Confirm Security Group Rules

**Objective**: Verify security group configuration

**Commands**:
```bash
# Get security group ID
SG_ID=$(terraform output -raw security_group_id)

# Describe security group
aws ec2 describe-security-groups --group-ids $SG_ID

# Check inbound rules
aws ec2 describe-security-groups --group-ids $SG_ID \
  --query 'SecurityGroups[0].IpPermissions'

# Check outbound rules
aws ec2 describe-security-groups --group-ids $SG_ID \
  --query 'SecurityGroups[0].IpPermissionsEgress'
```

**Expected Rules**:

**Inbound**:
- Port 22 (SSH) from your IP only
- Protocol: TCP
- Source: Your IP/32

**Outbound**:
- All traffic allowed
- Destination: 0.0.0.0/0

---

### 5.5 Validate Public IP Output

**Objective**: Verify instance has public IP and is accessible

**Commands**:
```bash
# Get public IP
PUBLIC_IP=$(terraform output -raw instance_public_ip)
echo "Public IP: $PUBLIC_IP"

# Get SSH command
SSH_CMD=$(terraform output -raw ssh_connection_command)
echo "SSH Command: $SSH_CMD"

# Test connectivity (if key available)
# ssh -i key.pem ec2-user@$PUBLIC_IP "echo 'Connection successful'"

# Verify DNS resolution
nslookup $PUBLIC_IP

# Check if port 22 is open (from your IP)
nc -zv $PUBLIC_IP 22
```

**Expected Results**:
- ✅ Public IP assigned
- ✅ IP is valid and routable
- ✅ SSH port accessible (from your IP)
- ✅ SSH command formatted correctly

---

### 5.6 Infrastructure Cleanup

**Objective**: Safely destroy test infrastructure

**Commands**:
```bash
# Plan destroy
terraform plan -destroy -var-file=test.tfvars

# Destroy infrastructure
terraform destroy -var-file=test.tfvars -auto-approve

# Verify cleanup
terraform show

# Check AWS (should return empty)
aws ec2 describe-instances --filters "Name=tag:Project,Values=GitWorkflowEnforcer" \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name]'
```

**Expected Results**:
- ✅ All resources destroyed
- ✅ State file shows no resources
- ✅ AWS shows no instances with project tag

---

