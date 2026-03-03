provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "GitWorkflowEnforcer"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}
