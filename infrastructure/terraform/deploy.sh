#!/bin/bash
# Deployment script for Git Workflow Enforcer EC2 instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Terraform
    if command -v terraform &> /dev/null; then
        TERRAFORM_VERSION=$(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4)
        print_success "Terraform installed (version $TERRAFORM_VERSION)"
    else
        print_error "Terraform not found. Please install Terraform."
        exit 1
    fi
    
    # Check AWS CLI
    if command -v aws &> /dev/null; then
        print_success "AWS CLI installed"
    else
        print_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    # Check AWS credentials
    if aws sts get-caller-identity &> /dev/null; then
        AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
        print_success "AWS credentials configured (Account: $AWS_ACCOUNT)"
    else
        print_error "AWS credentials not configured. Run 'aws configure'."
        exit 1
    fi
}

# Get user IP
get_user_ip() {
    print_header "Getting Your IP Address"
    
    USER_IP=$(curl -s ifconfig.me)
    if [ -z "$USER_IP" ]; then
        print_error "Failed to get your IP address"
        exit 1
    fi
    
    print_success "Your IP address: $USER_IP"
    echo "$USER_IP"
}

# Create terraform.tfvars if not exists
create_tfvars() {
    print_header "Configuring Variables"
    
    if [ ! -f terraform.tfvars ]; then
        print_info "terraform.tfvars not found. Creating from example..."
        
        if [ ! -f terraform.tfvars.example ]; then
            print_error "terraform.tfvars.example not found"
            exit 1
        fi
        
        cp terraform.tfvars.example terraform.tfvars
        
        # Get user IP
        USER_IP=$(get_user_ip)
        
        # Update my_ip in terraform.tfvars
        sed -i.bak "s|YOUR_IP_ADDRESS/32|${USER_IP}/32|g" terraform.tfvars
        rm -f terraform.tfvars.bak
        
        print_info "Please edit terraform.tfvars and set your key_name"
        print_info "Then run this script again"
        exit 0
    else
        print_success "terraform.tfvars found"
    fi
}

# Initialize Terraform
init_terraform() {
    print_header "Initializing Terraform"
    
    terraform init
    print_success "Terraform initialized"
}

# Validate configuration
validate_terraform() {
    print_header "Validating Configuration"
    
    terraform validate
    print_success "Configuration valid"
}

# Format Terraform files
format_terraform() {
    print_header "Formatting Terraform Files"
    
    terraform fmt -recursive
    print_success "Files formatted"
}

# Plan deployment
plan_deployment() {
    print_header "Planning Deployment"
    
    terraform plan -out=tfplan
    print_success "Plan created"
}

# Apply deployment
apply_deployment() {
    print_header "Applying Deployment"
    
    read -p "Do you want to apply this plan? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" = "yes" ]; then
        terraform apply tfplan
        rm -f tfplan
        print_success "Deployment complete!"
    else
        print_info "Deployment cancelled"
        rm -f tfplan
        exit 0
    fi
}

# Show outputs
show_outputs() {
    print_header "Deployment Outputs"
    
    terraform output
    
    echo ""
    print_info "To SSH into the instance, run:"
    terraform output -raw ssh_connection_command
    echo ""
}

# Main deployment flow
main() {
    print_header "Git Workflow Enforcer - EC2 Deployment"
    
    check_prerequisites
    create_tfvars
    init_terraform
    validate_terraform
    format_terraform
    plan_deployment
    apply_deployment
    show_outputs
    
    print_success "Deployment completed successfully!"
}

# Run main function
main
