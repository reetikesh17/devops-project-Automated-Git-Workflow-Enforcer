# Testing Guide - Git Workflow Enforcer

This guide walks you through testing all components of the Git Workflow Enforcer.

## Prerequisites Check

```bash
# Check Python installation
python --version

# Check Git installation
git --version

# Check Docker (if testing containers)
docker --version

# Check kubectl (if testing Kubernetes)
kubectl version --client
```

## 1. Test Core Validators

### Test Commit Validator

```bash
# Run the example test
python examples/test_commit_validator.py
```

Expected output: Shows validation results for various commit message formats.

### Test Branch Validator

```bash
# Run the example test
python examples/test_branch_validator.py
```

Expected output: Shows validation results for various branch name formats.

## 2. Test CLI Tool

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Test Commit Validation

```bash
# Test valid commit message
python -m src.main.cli validate-commit "feat: add new feature"

# Test invalid commit message
python -m src.main.cli validate-commit "bad commit message"
```

### Test Branch Validation

```bash
# Test valid branch name
python -m src.main.cli validate-branch "feature/new-feature"

# Test invalid branch name
python -m src.main.cli validate-branch "invalid_branch"
```

### Test with Config File

```bash
# Create a test config
echo '{
  "commit": {
    "max_length": 72,
    "min_length": 10,
    "require_scope": false
  },
  "branch": {
    "allowed_prefixes": ["feature/", "bugfix/", "hotfix/"]
  }
}' > test-config.json

# Test with config
python -m src.main.cli validate-commit "feat: test" --config test-config.json
```

## 3. Test Git Hooks

### Install Hooks

**On Linux/Mac:**
```bash
chmod +x install-hooks.sh
./install-hooks.sh
```

**On Windows:**
```bash
install-hooks.bat
```

### Test Pre-Commit Hook

```bash
# Make a change
echo "test" > test.txt
git add test.txt

# Try to commit with invalid message
git commit -m "bad message"
# Should fail

# Try with valid message
git commit -m "feat: add test file"
# Should succeed
```

### Test Commit-Msg Hook

```bash
# The commit-msg hook validates after you write the message
git commit -m "invalid"
# Should fail with validation error
```

### Test Pre-Push Hook

```bash
# Create a branch with invalid name
git checkout -b invalid_branch
# Try to push
git push origin invalid_branch
# Should fail

# Create valid branch
git checkout -b feature/test-branch
git push origin feature/test-branch
# Should succeed
```

### Uninstall Hooks

**On Linux/Mac:**
```bash
chmod +x uninstall-hooks.sh
./uninstall-hooks.sh
```

**On Windows:**
```bash
uninstall-hooks.bat
```

## 4. Test Docker

### Build Docker Image

```bash
docker build -t git-workflow-enforcer:test .
```

### Test Docker Container

```bash
# Test commit validation
docker run --rm git-workflow-enforcer:test validate-commit "feat: test feature"

# Test branch validation
docker run --rm git-workflow-enforcer:test validate-branch "feature/test"

# Test with custom config
docker run --rm -v ${PWD}/test-config.json:/app/config.json git-workflow-enforcer:test validate-commit "feat: test" --config /app/config.json
```

### Test Docker Compose

```bash
# Start services
docker-compose up -d

# Check logs
docker-compose logs

# Test the service
docker-compose exec validator python -m src.main.cli validate-commit "feat: test"

# Stop services
docker-compose down
```

## 5. Test GitHub Action

### Local Testing with act

```bash
# Install act (if not installed)
# https://github.com/nektos/act

# Test the workflow
act -j validate
```

### Test in GitHub Repository

1. Push your code to GitHub
2. Create a pull request
3. Check the Actions tab for workflow execution
4. Verify validation runs on commits and branches

## 6. Test CI/CD Pipelines

### Test GitLab CI

```bash
# If you have GitLab Runner locally
gitlab-runner exec docker validate_commits
gitlab-runner exec docker validate_branches
```

### Test GitHub Actions Workflow

```bash
# Push to trigger workflow
git push origin main

# Check workflow status
gh run list
gh run view <run-id>
```

## 7. Test Kubernetes Manifests

### Test Job (One-time validation)

```bash
# Apply the job
kubectl apply -f infrastructure/kubernetes/job.yaml

# Check status
kubectl get jobs
kubectl get pods

# View logs
kubectl logs -l app=git-workflow-enforcer

# Cleanup
kubectl delete -f infrastructure/kubernetes/job.yaml
```

### Test Deployment

```bash
# Apply deployment
kubectl apply -f infrastructure/kubernetes/deployment.yaml

# Check status
kubectl get deployments
kubectl get pods

# View logs
kubectl logs -l app=git-workflow-enforcer

# Test scaling
kubectl scale deployment git-workflow-enforcer --replicas=3
kubectl get pods

# Cleanup
kubectl delete -f infrastructure/kubernetes/deployment.yaml
```

### Test CronJob

```bash
# Apply cronjob
kubectl apply -f infrastructure/kubernetes/cronjob.yaml

# Check cronjob
kubectl get cronjobs

# Manually trigger a job from cronjob
kubectl create job --from=cronjob/git-workflow-enforcer-cron manual-test

# Check job status
kubectl get jobs
kubectl logs -l app=git-workflow-enforcer

# Cleanup
kubectl delete -f infrastructure/kubernetes/cronjob.yaml
kubectl delete job manual-test
```

## 8. Integration Tests

### Full Workflow Test

```bash
# 1. Install hooks
./install-hooks.sh  # or install-hooks.bat on Windows

# 2. Create a feature branch
git checkout -b feature/integration-test

# 3. Make changes
echo "Integration test" > integration-test.txt
git add integration-test.txt

# 4. Commit with valid message
git commit -m "feat: add integration test file"

# 5. Try invalid commit (should fail)
echo "More changes" >> integration-test.txt
git add integration-test.txt
git commit -m "bad commit"

# 6. Push branch (should succeed)
git push origin feature/integration-test

# 7. Try pushing invalid branch (should fail)
git checkout -b invalid_branch_name
git push origin invalid_branch_name

# 8. Cleanup
git checkout main
git branch -D feature/integration-test invalid_branch_name
```

## 9. Performance Tests

### Test with Large Commit Messages

```bash
# Generate large commit message
python -c "print('feat: ' + 'a' * 1000)" | xargs python -m src.main.cli validate-commit
```

### Test Batch Validation

```bash
# Create test script
cat > test_batch.sh << 'EOF'
#!/bin/bash
for i in {1..100}; do
  python -m src.main.cli validate-commit "feat: test commit $i"
done
EOF

chmod +x test_batch.sh
time ./test_batch.sh
```

## 10. Error Handling Tests

### Test Missing Dependencies

```bash
# Test without config file
python -m src.main.cli validate-commit "feat: test" --config nonexistent.json
```

### Test Invalid Input

```bash
# Empty commit message
python -m src.main.cli validate-commit ""

# Empty branch name
python -m src.main.cli validate-branch ""
```

## Troubleshooting

### Common Issues

1. **Hooks not executing**: Check file permissions with `ls -la .git/hooks/`
2. **Docker build fails**: Ensure all dependencies are in requirements.txt
3. **Kubernetes pods failing**: Check logs with `kubectl logs <pod-name>`
4. **Import errors**: Ensure you're running from project root

### Debug Mode

```bash
# Enable verbose output
export DEBUG=1
python -m src.main.cli validate-commit "feat: test"
```

## Success Criteria

✅ All validator tests pass
✅ CLI commands work with valid/invalid inputs
✅ Git hooks prevent invalid commits/branches
✅ Docker container runs successfully
✅ GitHub Action workflow completes
✅ Kubernetes manifests deploy without errors

## Quick Test All

Run this script to test everything quickly:

```bash
# Create quick test script
cat > quick-test.sh << 'EOF'
#!/bin/bash
set -e

echo "Testing validators..."
python examples/test_commit_validator.py
python examples/test_branch_validator.py

echo "Testing CLI..."
python -m src.main.cli validate-commit "feat: test feature"
python -m src.main.cli validate-branch "feature/test"

echo "Testing Docker..."
docker build -t git-workflow-enforcer:test . > /dev/null
docker run --rm git-workflow-enforcer:test validate-commit "feat: docker test"

echo "All tests passed! ✅"
EOF

chmod +x quick-test.sh
./quick-test.sh
```
