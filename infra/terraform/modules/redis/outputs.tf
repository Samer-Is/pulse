output "cluster_id" {
  description = "Redis cluster ID"
  value       = aws_elasticache_cluster.main.id
}

output "endpoint" {
  description = "Redis endpoint"
  value       = "${aws_elasticache_cluster.main.cache_nodes[0].address}:${aws_elasticache_cluster.main.cache_nodes[0].port}"
  sensitive   = true
}

output "address" {
  description = "Redis address"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
  sensitive   = true
}

output "port" {
  description = "Redis port"
  value       = aws_elasticache_cluster.main.cache_nodes[0].port
}

