# Quick Start Guide - Terraform EC2 Deployment

Get your Git Workflow Enforcer EC2 instance up and running in 5 minutes!

## Prerequisites

- AWS Account
- AWS CLI configured
- Terraform installed
- SSH key pair in AWS

## Step-by-Step Guide

### 1. Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `ap-south-1`
- Output format: `json`

### 2. Create SSH Key Pair

```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name git-workflow-enforcer-key \
  --query 'KeyMaterial' \
  --output text > git-workflow-enforcer-key.pem

# Set permissions (Linux/Mac)
chmod 400 git-workflow-enforcer-key.pem

# Windows: Right-click → Properties → Security → Advanced
```

### 3. Get Your IP Address

```bash
# Linux/Mac
curl ifconfig.me

# Windows PowerShell
(Invoke-WebRequest -Uri "https://ifconfig.me").Content
```

### 4. Configure Variables

```bash
# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit the file
nano terraform.tfvars  # or use your preferred editor
```

Update these values:
```hcl
key_name = "git-workflow-enforcer-key"
my_ip    = "YOUR_IP_ADDRESS/32"  # e.g., "203.0.113.25/32"
```

### 5. Deploy Infrastructure

#### Option A: Using Script (Recommended)

```bash
# Make script executable (Linux/Mac)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

#### Option B: Manual Commands

```bash
# Initialize
terraform init

# Validate
terraform validate

# Plan
terraform plan

# Apply
terraform apply
```

### 6. Get Connection Details

```bash
# View all outputs
terraform output

# Get SSH command
terraform output ssh_connection_command

# Get public IP
terraform output instance_public_ip
```

### 7. Connect to Instance

```bash
# Copy the SSH command from output
ssh -i git-workflow-enforcer-key.pem ec2-user@<PUBLIC_IP>
```

### 8. Setup Application

Once connected to the instance:

```bash
# Navigate to app directory
cd /opt/git-workflow-enforcer

# Clone repository
git clone https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer.git .

# Install dependencies
pip3 install -r requirements.txt

# Test validators
python3 examples/test_commit_validator.py
python3 examples/test_branch_validator.py

# Test CLI
python3 -m src.main.cli validate-commit "feat: test deployment"
```

## Using Makefile

```bash
# Initialize
make init

# Validate and format
make check

# Plan deployment
make plan

# Apply deployment
make apply

# Show outputs
make output

# SSH into instance
make ssh

# Destroy infrastructure
make destroy
```

## Common Commands

```bash
# Get instance IP
terraform output instance_public_ip

# Get instance ID
terraform output instance_id

# Refresh state
terraform refresh

# Show current state
terraform show

# List all resources
terraform state list
```

## Troubleshooting

### Can't Connect via SSH

1. Check your IP hasn't changed:
   ```bash
   curl ifconfig.me
   ```

2. Update terraform.tfvars with new IP:
   ```bash
   my_ip = "NEW_IP/32"
   ```

3. Apply changes:
   ```bash
   terraform apply
   ```

### Instance Not Ready

Wait a few minutes for user data script to complete:
```bash
# Check instance status
aws ec2 describe-instance-status --instance-ids $(terraform output -raw instance_id)
```

### Terraform Errors

```bash
# Refresh state
terraform refresh

# Re-initialize
rm -rf .terraform
terraform init
```

## Cleanup

### Destroy All Resources

```bash
# Using script
./destroy.sh

# Or manually
terraform destroy
```

## Cost

- **Free Tier**: First 12 months free (750 hours/month)
- **After Free Tier**: ~$9.30/month (ap-south-1)

## Next Steps

1. ✅ Instance deployed
2. ✅ Application installed
3. Configure Git hooks
4. Set up monitoring
5. Enable backups

## Support

- Documentation: See README.md
- Issues: GitHub Issues
- AWS Support: AWS Console

---

**Deployment Time**: ~5 minutes  
**Setup Time**: ~10 minutes  
**Total Time**: ~15 minutes
