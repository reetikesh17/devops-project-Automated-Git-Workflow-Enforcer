.PHONY: help init validate plan apply destroy clean fmt check output ssh

# Default target
help:
	@echo "Terraform Makefile for Git Workflow Enforcer"
	@echo ""
	@echo "Available targets:"
	@echo "  init      - Initialize Terraform"
	@echo "  validate  - Validate Terraform configuration"
	@echo "  fmt       - Format Terraform files"
	@echo "  check     - Run validation and formatting checks"
	@echo "  plan      - Show execution plan"
	@echo "  apply     - Apply Terraform configuration"
	@echo "  destroy   - Destroy all resources"
	@echo "  output    - Show all outputs"
	@echo "  ssh       - SSH into the instance"
	@echo "  clean     - Clean Terraform files"
	@echo ""

# Initialize Terraform
init:
	@echo "Initializing Terraform..."
	terraform init

# Validate configuration
validate:
	@echo "Validating Terraform configuration..."
	terraform validate

# Format Terraform files
fmt:
	@echo "Formatting Terraform files..."
	terraform fmt -recursive

# Check configuration
check: fmt validate
	@echo "Configuration check complete!"

# Show execution plan
plan:
	@echo "Generating execution plan..."
	terraform plan

# Apply configuration
apply:
	@echo "Applying Terraform configuration..."
	terraform apply

# Apply with auto-approve (use with caution)
apply-auto:
	@echo "Applying Terraform configuration (auto-approve)..."
	terraform apply -auto-approve

# Destroy all resources
destroy:
	@echo "Destroying all resources..."
	terraform destroy

# Destroy with auto-approve (use with caution)
destroy-auto:
	@echo "Destroying all resources (auto-approve)..."
	terraform destroy -auto-approve

# Show all outputs
output:
	@echo "Terraform outputs:"
	@terraform output

# Show specific output
output-ip:
	@terraform output -raw instance_public_ip

output-id:
	@terraform output -raw instance_id

output-ssh:
	@terraform output -raw ssh_connection_command

# SSH into instance
ssh:
	@echo "Connecting to instance..."
	@eval $$(terraform output -raw ssh_connection_command)

# Clean Terraform files
clean:
	@echo "Cleaning Terraform files..."
	rm -rf .terraform
	rm -f .terraform.lock.hcl
	rm -f terraform.tfstate
	rm -f terraform.tfstate.backup
	rm -f crash.log
	@echo "Clean complete!"

# Show Terraform version
version:
	@terraform version

# Refresh state
refresh:
	@echo "Refreshing Terraform state..."
	terraform refresh

# Show state
show:
	@echo "Showing Terraform state..."
	terraform show

# List resources
list:
	@echo "Listing Terraform resources..."
	terraform state list

# Get IP address
get-ip:
	@curl -s ifconfig.me
	@echo ""
