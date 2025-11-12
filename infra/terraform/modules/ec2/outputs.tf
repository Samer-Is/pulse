# EC2 Module Outputs

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.main.id
}

output "public_ip" {
  description = "Public IP address of EC2 instance"
  value       = aws_instance.main.public_ip
}

output "public_dns" {
  description = "Public DNS name of EC2 instance"
  value       = aws_instance.main.public_dns
}

output "instance_profile_arn" {
  description = "ARN of IAM instance profile"
  value       = aws_iam_instance_profile.ec2.arn
}

