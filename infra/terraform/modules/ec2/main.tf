# EC2 Module for Pulse AI Studio
# Creates t3.micro instance with Docker for cost optimization

terraform {
  required_version = ">= 1.6.0"
}

# Data source for latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM Role for EC2
resource "aws_iam_role" "ec2" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for EC2 (ECR, S3, SQS, Secrets Manager access)
resource "aws_iam_role_policy" "ec2" {
  name = "${var.project_name}-ec2-policy"
  role = aws_iam_role.ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = var.sqs_queue_arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "${var.secrets_arn_prefix}*"
      }
    ]
  })
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2.name

  tags = var.tags
}

# User Data Script to install Docker and setup environment
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -e
    
    # Update system
    dnf update -y
    
    # Install Docker
    dnf install -y docker
    systemctl start docker
    systemctl enable docker
    
    # Add ec2-user to docker group
    usermod -aG docker ec2-user
    
    # Install Docker Compose
    DOCKER_COMPOSE_VERSION="2.24.5"
    curl -L "https://github.com/docker/compose/releases/download/v$${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    # Install AWS CLI v2
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
    unzip -q /tmp/awscliv2.zip -d /tmp
    /tmp/aws/install
    rm -rf /tmp/aws /tmp/awscliv2.zip
    
    # Create application directory
    mkdir -p /srv/pulse
    chown ec2-user:ec2-user /srv/pulse
    
    # Install git
    dnf install -y git
    
    # Create helper script to pull secrets from Secrets Manager
    cat > /usr/local/bin/pulse-secrets.sh << 'SECRETSEOF'
    #!/bin/bash
    # Fetch secrets from AWS Secrets Manager and write to .env
    AWS_REGION="${var.aws_region}"
    SECRET_PREFIX="${var.project_name}"
    
    echo "Fetching secrets from AWS Secrets Manager..."
    
    # Function to get secret value
    get_secret() {
      aws secretsmanager get-secret-value \
        --region $AWS_REGION \
        --secret-id "$SECRET_PREFIX/$1" \
        --query SecretString \
        --output text 2>/dev/null || echo ""
    }
    
    # Write .env file
    cat > /srv/pulse/.env << ENVEOF
    NODE_ENV=production
    AWS_REGION=$AWS_REGION
    
    # Database
    POSTGRES_URL=$(get_secret "database-url")
    
    # S3
    S3_BUCKET_NAME=$(get_secret "s3-bucket-name")
    
    # SQS
    SQS_QUEUE_URL=$(get_secret "sqs-queue-url")
    
    # JWT
    JWT_SECRET=$(get_secret "jwt-secret")
    
    # OpenAI
    OPENAI_API_KEY=$(get_secret "openai-api-key")
    
    # Anthropic
    ANTHROPIC_API_KEY=$(get_secret "anthropic-api-key")
    
    # Google OAuth
    GOOGLE_OAUTH_CLIENT_ID=$(get_secret "google-oauth-client-id")
    GOOGLE_OAUTH_CLIENT_SECRET=$(get_secret "google-oauth-client-secret")
    
    # Google Vertex AI
    GCP_VERTEX_PROJECT_ID=$(get_secret "gcp-vertex-project-id")
    GCP_VERTEX_LOCATION=$(get_secret "gcp-vertex-location")
    GCP_VERTEX_SA_JSON=$(get_secret "gcp-vertex-sa-json")
    
    # Video providers
    RUNWAY_API_KEY=$(get_secret "runway-api-key")
    PIKA_API_KEY=$(get_secret "pika-api-key")
    ENVEOF
    
    chmod 600 /srv/pulse/.env
    chown ec2-user:ec2-user /srv/pulse/.env
    echo "Secrets fetched successfully"
    SECRETSEOF
    
    chmod +x /usr/local/bin/pulse-secrets.sh
    
    # Mark setup complete
    touch /var/log/pulse-setup-complete
    
    echo "EC2 setup completed successfully"
  EOF
}

# EC2 Instance
resource "aws_instance" "main" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name
  
  user_data = local.user_data

  root_block_device {
    volume_size           = var.root_volume_size
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-ec2"
    }
  )
}

# Elastic IP (optional - uncomment if needed for static IP)
# resource "aws_eip" "main" {
#   instance = aws_instance.main.id
#   domain   = "vpc"
#   
#   tags = merge(
#     var.tags,
#     {
#       Name = "${var.project_name}-eip"
#     }
#   )
# }

