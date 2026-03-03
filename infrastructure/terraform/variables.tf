# AWS Region
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-south-1"
}

# Instance Type
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"

  validation {
    condition     = can(regex("^t2\\.(micro|small|medium)$", var.instance_type))
    error_message = "Instance type must be t2.micro, t2.small, or t2.medium for free-tier eligibility."
  }
}

# Environment
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "Dev"

  validation {
    condition     = contains(["Dev", "Staging", "Production"], var.environment)
    error_message = "Environment must be Dev, Staging, or Production."
  }
}

# SSH Key Name
variable "key_name" {
  description = "Name of the SSH key pair to use for the instance"
  type        = string
  default     = ""
}

# My IP Address for SSH Access
variable "my_ip" {
  description = "Your IP address for SSH access (CIDR notation, e.g., 203.0.113.0/32)"
  type        = string

  validation {
    condition     = can(cidrhost(var.my_ip, 0))
    error_message = "Must be a valid CIDR notation (e.g., 203.0.113.0/32)."
  }
}

# Project Name
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "git-workflow-enforcer"
}
