# EC2 Instance Public IP
output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.git_workflow_enforcer.public_ip
}

# EC2 Instance ID
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.git_workflow_enforcer.id
}

# EC2 Instance Public DNS
output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.git_workflow_enforcer.public_dns
}

# Security Group ID
output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.git_workflow_enforcer.id
}

# AMI ID Used
output "ami_id" {
  description = "AMI ID used for the instance"
  value       = data.aws_ami.amazon_linux_2.id
}

# SSH Connection Command
output "ssh_connection_command" {
  description = "Command to SSH into the instance"
  value       = var.key_name != "" ? "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_instance.git_workflow_enforcer.public_ip}" : "No key pair specified"
}

# Instance State
output "instance_state" {
  description = "Current state of the instance"
  value       = aws_instance.git_workflow_enforcer.instance_state
}
