# Terraform Configuration for Git Workflow Enforcer

This Terraform configuration provisions an EC2 instance on AWS for the Git Workflow Enforcer project.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** installed (>= 1.0)
3. **AWS CLI** configured with credentials
4. **SSH Key Pair** created in AWS

## Quick Start

### 1. Configure AWS Credentials

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment Variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ap-south-1"
```

### 2. Create SSH Key Pair

```bash
# Create key pair in AWS
aws ec2 create-key-pair \
  --key-name git-workflow-enforcer-key \
  --query 'KeyMaterial' \
  --output text > git-workflow-enforcer-key.pem

# Set permissions
chmod 400 git-workflow-enforcer-key.pem
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

# Edit with your values
nano terraform.tfvars
```

Update `terraform.tfvars`:
```hcl
aws_region    = "ap-south-1"
instance_type = "t2.micro"
environment   = "Dev"
key_name      = "git-workflow-enforcer-key"
my_ip         = "YOUR_IP_ADDRESS/32"  # e.g., "203.0.113.25/32"
project_name  = "git-workflow-enforcer"
```

### 5. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Preview changes
terraform plan

# Apply configuration
terraform apply
```

### 6. Connect to Instance

```bash
# Get connection command from output
terraform output ssh_connection_command

# Or manually
ssh -i git-workflow-enforcer-key.pem ec2-user@<PUBLIC_IP>
```

## Configuration Details

### Resources Created

1. **EC2 Instance**
   - Amazon Linux 2 (latest AMI)
   - Instance type: t2.micro (free-tier eligible)
   - 8GB GP3 EBS volume (encrypted)
   - IMDSv2 enabled
   - Detailed monitoring enabled

2. **Security Group**
   - Inbound: SSH (22) from your IP only
   - Outbound: All traffic allowed

3. **User Data Script**
   - System updates
   - Git installation
   - Python 3 installation
   - Docker installation
   - Docker Compose installation

### Default VPC

This configuration uses the default VPC in your AWS account. No new VPC is created.

## Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region | `ap-south-1` | No |
| `instance_type` | EC2 instance type | `t2.micro` | No |
| `environment` | Environment name | `Dev` | No |
| `key_name` | SSH key pair name | `""` | Yes |
| `my_ip` | Your IP for SSH (CIDR) | - | Yes |
| `project_name` | Project name | `git-workflow-enforcer` | No |

## Outputs

| Output | Description |
|--------|-------------|
| `instance_public_ip` | Public IP address |
| `instance_id` | EC2 instance ID |
| `instance_public_dns` | Public DNS name |
| `security_group_id` | Security group ID |
| `ami_id` | AMI ID used |
| `ssh_connection_command` | SSH command |
| `instance_state` | Instance state |

## View Outputs

```bash
# All outputs
terraform output

# Specific output
terraform output instance_public_ip

# JSON format
terraform output -json
```

## Post-Deployment Setup

### 1. Connect to Instance

```bash
ssh -i git-workflow-enforcer-key.pem ec2-user@$(terraform output -raw instance_public_ip)
```

### 2. Clone Repository

```bash
cd /opt/git-workflow-enforcer
git clone https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer.git .
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Build Docker image
docker build -t git-workflow-enforcer:latest .
```

### 4. Run Tests

```bash
# Run validator tests
python3 examples/test_commit_validator.py
python3 examples/test_branch_validator.py

# Test CLI
python3 -m src.main.cli validate-commit "feat: test deployment"
```

## Cost Estimation

### Free Tier Eligible (First 12 Months)

- **EC2 t2.micro**: 750 hours/month (free)
- **EBS Storage**: 30 GB (8 GB used, free)
- **Data Transfer**: 15 GB outbound (free)

### After Free Tier

- **EC2 t2.micro**: ~$8.50/month (ap-south-1)
- **EBS GP3**: ~$0.80/month (8 GB)
- **Total**: ~$9.30/month

## Security Best Practices

✅ **Implemented**:
- IMDSv2 required (prevents SSRF attacks)
- EBS encryption enabled
- SSH restricted to your IP only
- Security group with minimal permissions
- No hardcoded credentials
- Latest Amazon Linux 2 AMI
- Detailed monitoring enabled

⚠️ **Additional Recommendations**:
- Rotate SSH keys regularly
- Enable AWS CloudTrail
- Set up CloudWatch alarms
- Use AWS Systems Manager Session Manager
- Implement backup strategy
- Enable VPC Flow Logs

## Maintenance

### Update Instance

```bash
# SSH into instance
ssh -i git-workflow-enforcer-key.pem ec2-user@<PUBLIC_IP>

# Update system
sudo yum update -y

# Update application
cd /opt/git-workflow-enforcer
git pull origin main
```

### Modify Infrastructure

```bash
# Edit variables
nano terraform.tfvars

# Preview changes
terraform plan

# Apply changes
terraform apply
```

### Destroy Infrastructure

```bash
# Preview destruction
terraform plan -destroy

# Destroy all resources
terraform destroy
```

## Troubleshooting

### Cannot Connect via SSH

1. **Check Security Group**:
   ```bash
   terraform output security_group_id
   aws ec2 describe-security-groups --group-ids <SG_ID>
   ```

2. **Verify Your IP**:
   ```bash
   curl ifconfig.me
   # Update terraform.tfvars if IP changed
   terraform apply
   ```

3. **Check Instance State**:
   ```bash
   terraform output instance_state
   aws ec2 describe-instances --instance-ids <INSTANCE_ID>
   ```

### User Data Script Failed

```bash
# SSH into instance
ssh -i git-workflow-enforcer-key.pem ec2-user@<PUBLIC_IP>

# Check user data logs
sudo cat /var/log/cloud-init-output.log
sudo cat /var/log/user-data.log
```

### Terraform State Issues

```bash
# Refresh state
terraform refresh

# Import existing resource
terraform import aws_instance.git_workflow_enforcer <INSTANCE_ID>

# Remove from state (if needed)
terraform state rm aws_instance.git_workflow_enforcer
```

## Advanced Usage

### Multiple Environments

```bash
# Create workspace for staging
terraform workspace new staging
terraform workspace select staging
terraform apply -var-file="staging.tfvars"

# Switch to production
terraform workspace new production
terraform workspace select production
terraform apply -var-file="production.tfvars"
```

### Remote State (S3 Backend)

Add to `versions.tf`:
```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "git-workflow-enforcer/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### Custom AMI

```hcl
# In main.tf, replace data source with:
variable "custom_ami_id" {
  description = "Custom AMI ID"
  type        = string
  default     = "ami-xxxxxxxxx"
}

resource "aws_instance" "git_workflow_enforcer" {
  ami = var.custom_ami_id
  # ... rest of configuration
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Terraform Deploy

on:
  push:
    branches: [main]
    paths:
      - 'infrastructure/terraform/**'

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        
      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/terraform
        
      - name: Terraform Plan
        run: terraform plan
        working-directory: infrastructure/terraform
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer/issues
- Documentation: See main README.md

## License

This Terraform configuration is part of the Git Workflow Enforcer project.
See LICENSE file for details.
