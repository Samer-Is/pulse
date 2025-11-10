# Terraform backend configuration
# S3 bucket and DynamoDB table will be created automatically on first apply

terraform {
  backend "s3" {
    bucket         = "ai-studio-tfstate"
    key            = "terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "ai-studio-tfstate-lock"
    encrypt        = true
  }
}
