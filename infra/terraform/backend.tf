# Terraform backend configuration
# Using local backend for initial deployment
# After infrastructure is created, migrate to S3 backend

terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}

# After first apply, uncomment this and run: terraform init -migrate-state
# terraform {
#   backend "s3" {
#     bucket         = "pulse-ai-studio-tfstate"
#     key            = "terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "terraform-locks"
#     encrypt        = true
#   }
# }
