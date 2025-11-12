# Dev Environment Outputs

# EC2 Outputs
output "ec2_public_ip" {
  description = "Public IP of EC2 instance"
  value       = module.ec2.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of EC2 instance"
  value       = module.ec2.public_dns
}

output "ssh_command" {
  description = "SSH command to connect to EC2"
  value       = "ssh -i your-key.pem ec2-user@${module.ec2.public_dns}"
}

# RDS Outputs
output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.db_endpoint
}

output "database_name" {
  description = "Database name"
  value       = module.rds.db_name
}

output "database_connection_string" {
  description = "Database connection string (sensitive)"
  value       = module.rds.connection_string
  sensitive   = true
}

# S3 Outputs
output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.s3.bucket_name
}

# SQS Outputs
output "sqs_queue_url" {
  description = "SQS queue URL"
  value       = module.sqs.queue_url
}

output "sqs_dlq_url" {
  description = "SQS Dead Letter Queue URL"
  value       = module.sqs.dlq_url
}

# ECR Outputs
output "ecr_repository_urls" {
  description = "ECR repository URLs"
  value       = module.ecr.repository_urls
}

output "ecr_registry_id" {
  description = "ECR registry ID"
  value       = module.ecr.registry_id
}

# Secrets Outputs
output "secrets_info" {
  description = "Information about created secrets"
  value       = "Secrets created in AWS Secrets Manager under prefix '${var.project_name}/'"
}

# Deployment Instructions
output "next_steps" {
  description = "Next steps after infrastructure deployment"
  value       = <<-EOT
    
    ✅ Infrastructure deployed successfully!
    
    Next steps:
    
    1. SSH to EC2:
       ssh -i your-key.pem ec2-user@${module.ec2.public_dns}
    
    2. Update secrets in AWS Secrets Manager:
       - ${var.project_name}/openai-api-key
       - ${var.project_name}/anthropic-api-key
       - ${var.project_name}/google-oauth-client-id
       - ${var.project_name}/google-oauth-client-secret
       - ${var.project_name}/gcp-vertex-project-id
       - ${var.project_name}/gcp-vertex-sa-json
       - ${var.project_name}/runway-api-key
       - ${var.project_name}/pika-api-key
    
    3. On EC2, setup application:
       cd /srv/pulse
       git clone https://github.com/Samer-Is/pulse.git .
       /usr/local/bin/pulse-secrets.sh  # Fetch secrets
       
       # Login to ECR
       aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${module.ecr.registry_id}.dkr.ecr.${var.aws_region}.amazonaws.com
       
       # Pull and run containers
       docker-compose -f docker-compose.prod.yml up -d
    
    4. Application will be available at:
       http://${module.ec2.public_dns}
    
    ECR Repositories:
    ${join("\n", [for k, v in module.ecr.repository_urls : "  - ${k}: ${v}"])}
  EOT
}

