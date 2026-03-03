# Terraform Deployment Guide - Git Workflow Enforcer

## 🎯 Overview

Production-ready Terraform configuration for deploying Git Workflow Enforcer on AWS EC2.

**Location**: `infrastructure/terraform/`

## 📁 Files Created

```
infrastructure/terraform/
├── versions.tf                  # Terraform & provider versions
├── provider.tf                  # AWS provider configuration
├── variables.tf                 # Input variables (validated)
├── main.tf                      # Infrastructure resources
├── outputs.tf                   # Output values
├── terraform.tfvars.example     # Example configuration
├── .gitignore                   # Git ignore patterns
├── README.md                    # Complete documentation (detailed)
├── QUICKSTART.md               # 5-minute quick start
├── TERRAFORM-SUMMARY.md        # Configuration summary
├── Makefile                     # Automation commands
├── deploy.sh                    # Automated deployment script
└── destroy.sh                   # Cleanup script
```

## ✨ Features

### Infrastructure
- ✅ EC2 instance (t2.micro - free tier eligible)
- ✅ Amazon Linux 2 (latest AMI, auto-updated)
- ✅ Security group (SSH from your IP only)
- ✅ 8GB encrypted EBS volume
- ✅ Uses default VPC (no new VPC created)

### Security
- ✅ IMDSv2 required (prevents SSRF attacks)
- ✅ EBS encryption enabled
- ✅ SSH restricted to your IP
- ✅ No hardcoded credentials
- ✅ Detailed monitoring enabled

### Automation
- ✅ User data script (installs Git, Python, Docker)
- ✅ Deployment script (deploy.sh)
- ✅ Cleanup script (destroy.sh)
- ✅ Makefile for common tasks
- ✅ Input validation

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites

```bash
# Check installations
terraform --version  # >= 1.0
aws --version       # AWS CLI
aws sts get-caller-identity  # Verify credentials
```

### 2. Create SSH Key

```bash
aws ec2 create-key-pair \
  --key-name git-workflow-enforcer-key \
  --query 'KeyMaterial' \
  --output text > git-workflow-enforcer-key.pem

chmod 400 git-workflow-enforcer-key.pem
```

### 3. Configure Variables

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
key_name = "git-workflow-enforcer-key"
my_ip    = "YOUR_IP/32"  # Get with: curl ifconfig.me
```

### 4. Deploy

```bash
# Option A: Using script (recommended)
./deploy.sh

# Option B: Manual
terraform init
terraform plan
terraform apply
```

### 5. Connect

```bash
# Get SSH command
terraform output ssh_connection_command

# Connect
ssh -i git-workflow-enforcer-key.pem ec2-user@<PUBLIC_IP>
```

## 📋 Configuration Details

### Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `aws_region` | `ap-south-1` | No | AWS region |
| `instance_type` | `t2.micro` | No | Instance type |
| `environment` | `Dev` | No | Environment |
| `key_name` | - | Yes | SSH key name |
| `my_ip` | - | Yes | Your IP (CIDR) |
| `project_name` | `git-workflow-enforcer` | No | Project name |

### Outputs

- `instance_public_ip` - Public IP address
- `instance_id` - EC2 instance ID
- `instance_public_dns` - Public DNS name
- `security_group_id` - Security group ID
- `ami_id` - AMI ID used
- `ssh_connection_command` - SSH command
- `instance_state` - Instance state

## 💰 Cost Estimate

### Free Tier (First 12 Months)
- EC2 t2.micro: 750 hours/month - **FREE**
- EBS 8GB: Within 30GB limit - **FREE**
- Data Transfer: Within 15GB limit - **FREE**

**Total**: $0/month

### After Free Tier (ap-south-1)
- EC2 t2.micro: ~$8.50/month
- EBS GP3 8GB: ~$0.80/month

**Total**: ~$9.30/month

## 🛠️ Usage

### Using Makefile

```bash
make init      # Initialize Terraform
make check     # Validate & format
make plan      # Show execution plan
make apply     # Deploy infrastructure
make output    # Show all outputs
make ssh       # SSH into instance
make destroy   # Destroy all resources
```

### Manual Commands

```bash
# Initialize
terraform init

# Validate
terraform validate

# Format
terraform fmt -recursive

# Plan
terraform plan

# Apply
terraform apply

# Show outputs
terraform output

# Destroy
terraform destroy
```

## 📖 Documentation

### Quick Reference
- **QUICKSTART.md** - 5-minute deployment guide
- **README.md** - Complete documentation with examples
- **TERRAFORM-SUMMARY.md** - Configuration overview

### Key Sections in README.md
1. Prerequisites & Setup
2. Configuration Guide
3. Deployment Steps
4. Post-Deployment Setup
5. Security Best Practices
6. Troubleshooting
7. Advanced Usage
8. CI/CD Integration

## 🔒 Security Best Practices

### Implemented
✅ IMDSv2 required  
✅ EBS encryption  
✅ SSH from specific IP only  
✅ No hardcoded credentials  
✅ Latest AMI (auto-updated)  
✅ Minimal security group rules  
✅ Detailed monitoring  

### Recommended
- Rotate SSH keys regularly
- Enable AWS CloudTrail
- Set up CloudWatch alarms
- Use AWS Systems Manager Session Manager
- Implement backup strategy
- Enable VPC Flow Logs

## 🔧 Post-Deployment

### 1. Connect to Instance

```bash
ssh -i git-workflow-enforcer-key.pem ec2-user@<PUBLIC_IP>
```

### 2. Install Application

```bash
cd /opt/git-workflow-enforcer
git clone https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer.git .
pip3 install -r requirements.txt
```

### 3. Verify Installation

```bash
# Test validators
python3 examples/test_commit_validator.py
python3 examples/test_branch_validator.py

# Test CLI
python3 -m src.main.cli validate-commit "feat: test deployment"
python3 -m src.main.cli validate-branch "feature/TEST-123-test"

# Build Docker image
docker build -t git-workflow-enforcer:latest .
```

## 🐛 Troubleshooting

### Can't Connect via SSH

```bash
# Check your current IP
curl ifconfig.me

# Update terraform.tfvars if IP changed
my_ip = "NEW_IP/32"

# Apply changes
terraform apply
```

### Terraform Errors

```bash
# Refresh state
terraform refresh

# Re-initialize
rm -rf .terraform
terraform init
```

### Instance Not Ready

```bash
# Check instance status
aws ec2 describe-instance-status \
  --instance-ids $(terraform output -raw instance_id)

# Check user data logs (after SSH)
sudo cat /var/log/cloud-init-output.log
```

## 🔄 Maintenance

### Update Infrastructure

```bash
# Edit variables
nano terraform.tfvars

# Preview changes
terraform plan

# Apply changes
terraform apply
```

### Update Application

```bash
# SSH into instance
ssh -i key.pem ec2-user@<IP>

# Update system
sudo yum update -y

# Update application
cd /opt/git-workflow-enforcer
git pull origin main
```

### Backup State

```bash
# Local backup
cp terraform.tfstate terraform.tfstate.backup

# Or use S3 backend (see README.md)
```

## 🗑️ Cleanup

### Destroy All Resources

```bash
# Using script
./destroy.sh

# Or manually
terraform destroy

# Verify cleanup
aws ec2 describe-instances --filters "Name=tag:Project,Values=GitWorkflowEnforcer"
```

## 🚀 Advanced Usage

### Multiple Environments

```bash
# Create workspaces
terraform workspace new staging
terraform workspace new production

# Deploy to staging
terraform workspace select staging
terraform apply -var-file="staging.tfvars"

# Deploy to production
terraform workspace select production
terraform apply -var-file="production.tfvars"
```

### Remote State (S3)

Add to `versions.tf`:
```hcl
terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "git-workflow-enforcer/terraform.tfstate"
    region = "ap-south-1"
    encrypt = true
  }
}
```

### CI/CD Integration

See README.md for GitHub Actions and GitLab CI examples.

## ✅ Validation Checklist

Before deployment:
- [ ] AWS credentials configured
- [ ] SSH key pair created
- [ ] Your IP address obtained
- [ ] terraform.tfvars configured
- [ ] Terraform initialized

After deployment:
- [ ] Instance running
- [ ] SSH connection working
- [ ] Application installed
- [ ] Tests passing
- [ ] Docker working

## 📊 Resource Tags

All resources are tagged with:
- `Name` - Resource identifier
- `Project` - "GitWorkflowEnforcer"
- `Environment` - Dev/Staging/Production
- `ManagedBy` - "Terraform"

## 🎓 Learning Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

## 📞 Support

- **Documentation**: See README.md in terraform directory
- **Issues**: GitHub Issues
- **AWS Support**: AWS Console

## 🎉 Summary

✅ **Production-ready Terraform configuration**  
✅ **Complete documentation**  
✅ **Automated deployment scripts**  
✅ **Security best practices**  
✅ **Free-tier eligible**  
✅ **Easy to use and maintain**

---

**Status**: Ready for Deployment  
**Deployment Time**: ~5 minutes  
**Setup Time**: ~10 minutes  
**Total Time**: ~15 minutes

**Next Step**: Navigate to `infrastructure/terraform/` and follow QUICKSTART.md
