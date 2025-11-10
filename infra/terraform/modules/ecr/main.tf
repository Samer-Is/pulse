# ECR Module - Container registries for all services

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# ECR Repositories
resource "aws_ecr_repository" "repos" {
  for_each = toset(var.repositories)

  name                 = "${local.name_prefix}-${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name = "${local.name_prefix}-${each.key}"
  }
}

# Lifecycle Policy (keep last 10 images)
resource "aws_ecr_lifecycle_policy" "policy" {
  for_each   = toset(var.repositories)
  repository = aws_ecr_repository.repos[each.key].name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

