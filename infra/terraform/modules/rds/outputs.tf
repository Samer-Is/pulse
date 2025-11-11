output "cluster_id" {
  description = "RDS instance identifier"
  value       = aws_db_instance.main.id
}

output "cluster_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "cluster_reader_endpoint" {
  description = "RDS instance endpoint (no reader for single instance)"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "master_username" {
  description = "Master username"
  value       = aws_db_instance.main.username
  sensitive   = true
}
