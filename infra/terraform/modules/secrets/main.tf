# Secrets Manager Module - Placeholder secrets for application

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  secrets = {
    # Database
    "AI_STUDIO_DATABASE_URL" = "PLACEHOLDER - Will be populated by RDS module"
    "AI_STUDIO_REDIS_URL"    = "PLACEHOLDER - Will be populated by Redis module"
    
    # JWT
    "AI_STUDIO_JWT_SECRET" = "PLACEHOLDER - Generate with: openssl rand -hex 32"
    
    # Email
    "AI_STUDIO_EMAIL_FROM" = "noreply@your-domain.tld"
    "AI_STUDIO_SES_REGION" = var.aws_region
    
    # AI Providers
    "OPENAI_API_KEY"       = "PLACEHOLDER - Add your OpenAI key"
    "ANTHROPIC_API_KEY"    = "PLACEHOLDER - Add your Anthropic key"
    "GOOGLE_API_KEY"       = "PLACEHOLDER - Add your Google key"
    "REPLICATE_API_TOKEN"  = "PLACEHOLDER - Add your Replicate token"
    
    # Nano Banana
    "NANO_BANANA_API_KEY"  = "PLACEHOLDER - Add your Nano Banana key"
    "NANO_BANANA_BASE_URL" = "https://api.nanobanana.ai/v1"
    
    # Veo3
    "VEO3_API_KEY"  = "PLACEHOLDER - Add your Veo3 key"
    "VEO3_BASE_URL" = "https://api.veo3.ai/v1"
    
    # Payments
    "AI_STUDIO_HYPERPAY_API_KEY"  = "PLACEHOLDER - Add your HyperPay key"
    "AI_STUDIO_HYPERPAY_ENTITY_ID" = "PLACEHOLDER - Add your HyperPay entity ID"
    "AI_STUDIO_HYPERPAY_TEST_MODE" = "true"
    
    # S3
    "AI_STUDIO_S3_ASSETS" = var.assets_bucket_name
    "AI_STUDIO_S3_QUAR"   = var.quarantine_bucket_name
  }
}

# Create secrets
resource "aws_secretsmanager_secret" "secrets" {
  for_each = local.secrets

  name        = each.key
  description = "Secret for ${each.key}"

  tags = {
    Name = each.key
  }
}

# Populate initial values
resource "aws_secretsmanager_secret_version" "secrets" {
  for_each = local.secrets

  secret_id     = aws_secretsmanager_secret.secrets[each.key].id
  secret_string = each.value
}

