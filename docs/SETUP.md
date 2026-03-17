# Setup Guide

## Prerequisites

- Python 3.11+
- Git
- Docker (optional)
- kubectl (optional)
- Terraform (optional)

## Local Setup

```bash
git clone https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer.git
cd devops-project-Automated-Git-Workflow-Enforcer
pip install -r requirements.txt
```

Install Git hooks:
```bash
install-hooks.bat    # Windows
./install-hooks.sh   # Linux/macOS
```

Verify:
```bash
python -m src.main.cli validate-commit "feat: test installation"
```

## Docker

```bash
docker build -t git-workflow-enforcer:latest .
docker run --rm git-workflow-enforcer:latest python -m src.main.cli validate-commit "feat: test"
```

## Kubernetes

```bash
kubectl apply -f infrastructure/kubernetes/configmap.yaml
kubectl apply -f infrastructure/kubernetes/job.yaml
```

## Terraform

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS credentials
terraform init
terraform plan
terraform apply
```

## Web Dashboard

```bash
python ui/app.py
# Open http://localhost:5000
# Login: admin / admin123
```
