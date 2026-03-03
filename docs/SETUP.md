# Setup Guide

## Prerequisites

- Python 3.11+
- Git
- Docker (optional)
- Kubernetes (optional)
- Terraform (optional)
- AWS CLI (for Terraform)

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer.git
cd devops-project-Automated-Git-Workflow-Enforcer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Git Hooks

**Linux/Mac**:
```bash
chmod +x install-hooks.sh
./install-hooks.sh
```

**Windows**:
```bash
install-hooks.bat
```

### 4. Test Installation

```bash
python -m src.main.cli validate-commit "feat: test installation"
```

## Docker Setup

```bash
# Build image
docker build -t git-workflow-enforcer:latest .

# Run validation
docker run --rm git-workflow-enforcer:latest \
  python -m src.main.cli validate-commit "feat: test"
```

## Kubernetes Setup

```bash
# Apply ConfigMap
kubectl apply -f infrastructure/kubernetes/configmap.yaml

# Deploy Job
kubectl apply -f infrastructure/kubernetes/job.yaml
```

## Terraform Setup

```bash
cd infrastructure/terraform

# Initialize
terraform init

# Configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars

# Deploy
terraform plan
terraform apply
```

## Verification

```bash
# Run tests
python examples/test_commit_validator.py
python examples/test_branch_validator.py

# Run all tests
./test-all.sh  # Linux/Mac
test-all.bat   # Windows
```
