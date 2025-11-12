# ECR Module for Pulse AI Studio
# Creates container repositories for web, api, and workers

terraform {
  required_version = ">= 1.6.0"
}

# ECR Repositories
locals {
  repositories = ["web", "api", "workers"]
}

resource "aws_ecr_repository" "repos" {
  for_each = toset(local.repositories)

  name                 = "${var.project_name}-${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${each.key}"
    }
  )
}

# Lifecycle policy to manage image retention
resource "aws_ecr_lifecycle_policy" "repos" {
  for_each = aws_ecr_repository.repos

  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last ${var.max_image_count} images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = var.max_image_count
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Repository policy (allow EC2 to pull)
resource "aws_ecr_repository_policy" "repos" {
  for_each = aws_ecr_repository.repos

  repository = each.value.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPull"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
        Condition = {
          StringEquals = {
            "aws:PrincipalAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

