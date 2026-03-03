# Data source to get the default VPC
data "aws_vpc" "default" {
  default = true
}

# Data source to get the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

# Security Group for EC2 Instance
resource "aws_security_group" "git_workflow_enforcer" {
  name        = "${var.project_name}-sg"
  description = "Security group for Git Workflow Enforcer EC2 instance"
  vpc_id      = data.aws_vpc.default.id

  # Inbound SSH from my IP only
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  # Outbound all traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# EC2 Instance
resource "aws_instance" "git_workflow_enforcer" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type
  key_name      = var.key_name != "" ? var.key_name : null

  vpc_security_group_ids = [aws_security_group.git_workflow_enforcer.id]

  # User data script to install dependencies
  user_data = <<-EOF
              #!/bin/bash
              set -e
              
              # Update system
              yum update -y
              
              # Install Git
              yum install -y git
              
              # Install Python 3
              yum install -y python3 python3-pip
              
              # Install Docker
              amazon-linux-extras install docker -y
              systemctl start docker
              systemctl enable docker
              usermod -a -G docker ec2-user
              
              # Install Docker Compose
              curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              
              # Create application directory
              mkdir -p /opt/git-workflow-enforcer
              chown ec2-user:ec2-user /opt/git-workflow-enforcer
              
              # Log completion
              echo "Git Workflow Enforcer instance setup completed" > /var/log/user-data.log
              EOF

  # Root volume configuration
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 8
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-root-volume"
    }
  }

  # Instance metadata options (IMDSv2)
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  # Monitoring
  monitoring = true

  tags = {
    Name        = var.project_name
    Project     = "GitWorkflowEnforcer"
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [
      ami,
      user_data
    ]
  }
}
