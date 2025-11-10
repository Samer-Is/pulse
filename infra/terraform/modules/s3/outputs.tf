output "assets_bucket_name" {
  description = "Name of assets S3 bucket"
  value       = aws_s3_bucket.assets.id
}

output "assets_bucket_arn" {
  description = "ARN of assets S3 bucket"
  value       = aws_s3_bucket.assets.arn
}

output "quarantine_bucket_name" {
  description = "Name of quarantine S3 bucket"
  value       = aws_s3_bucket.quarantine.id
}

output "quarantine_bucket_arn" {
  description = "ARN of quarantine S3 bucket"
  value       = aws_s3_bucket.quarantine.arn
}

output "tfstate_bucket_name" {
  description = "Name of Terraform state S3 bucket"
  value       = aws_s3_bucket.tfstate.id
}

output "tfstate_dynamodb_table_name" {
  description = "Name of DynamoDB table for state locking"
  value       = aws_dynamodb_table.tfstate_lock.name
}

