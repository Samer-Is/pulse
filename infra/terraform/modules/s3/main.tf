# S3 Module for Pulse AI Studio
# Creates bucket for exports (CV, slides, images, videos)

terraform {
  required_version = ">= 1.6.0"
}

# S3 Bucket
resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-${var.environment}-exports"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-exports"
    }
  )
}

# Block public access
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Lifecycle rules to manage costs
resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "delete-old-exports"
    status = "Enabled"

    # Delete files older than 90 days
    expiration {
      days = var.object_expiration_days
    }

    # Move to Intelligent-Tiering after 30 days (optional)
    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }
  }

  rule {
    id     = "abort-incomplete-multipart-uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# CORS configuration for web uploads
resource "aws_s3_bucket_cors_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE"]
    allowed_origins = var.allowed_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

