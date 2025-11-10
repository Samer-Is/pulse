# CloudFront Module - CDN for static assets and API caching

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Origin Access Control for S3
resource "aws_cloudfront_origin_access_control" "s3" {
  count = var.s3_bucket_name != "" ? 1 : 0

  name                              = "${local.name_prefix}-s3-oac"
  description                       = "OAC for S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${local.name_prefix} CDN"
  default_root_object = "index.html"
  aliases             = var.domain_aliases
  price_class         = var.price_class

  # ALB Origin (Frontend)
  origin {
    domain_name = var.alb_dns_name
    origin_id   = "alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = var.certificate_arn != "" ? "https-only" : "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # S3 Origin (Static Assets)
  dynamic "origin" {
    for_each = var.s3_bucket_name != "" ? [1] : []
    content {
      domain_name              = "${var.s3_bucket_name}.s3.${var.aws_region}.amazonaws.com"
      origin_id                = "s3"
      origin_access_control_id = aws_cloudfront_origin_access_control.s3[0].id
    }
  }

  # Default behavior (ALB)
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "alb"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = true
      headers      = ["Host", "Authorization", "Accept-Language"]

      cookies {
        forward = "all"
      }
    }

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # Static assets behavior (S3)
  dynamic "ordered_cache_behavior" {
    for_each = var.s3_bucket_name != "" ? [1] : []
    content {
      path_pattern           = "/assets/*"
      allowed_methods        = ["GET", "HEAD", "OPTIONS"]
      cached_methods         = ["GET", "HEAD"]
      target_origin_id       = "s3"
      viewer_protocol_policy = "redirect-to-https"
      compress               = true

      forwarded_values {
        query_string = false
        cookies {
          forward = "none"
        }
      }

      min_ttl     = 0
      default_ttl = 86400  # 1 day
      max_ttl     = 604800 # 7 days
    }
  }

  # Custom error responses
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # TLS certificate
  viewer_certificate {
    acm_certificate_arn      = var.certificate_arn != "" ? var.certificate_arn : null
    ssl_support_method       = var.certificate_arn != "" ? "sni-only" : null
    minimum_protocol_version = var.certificate_arn != "" ? "TLSv1.2_2021" : null
    cloudfront_default_certificate = var.certificate_arn == ""
  }

  tags = {
    Name = "${local.name_prefix}-cloudfront"
  }
}

