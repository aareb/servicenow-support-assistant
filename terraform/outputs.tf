output "ecr_repository_url" {
  value       = aws_ecr_repository.backend.repository_url
  description = "ECR repository URL for backend image deployment"
}

output "frontend_s3_bucket" {
  value       = aws_s3_bucket.frontend.bucket
  description = "Frontend S3 bucket name"
}

output "cloudfront_domain_name" {
  value       = aws_cloudfront_distribution.frontend.domain_name
  description = "CloudFront domain name for frontend delivery"
}

output "alb_dns_name" {
  value       = aws_lb.frontend.dns_name
  description = "Application Load Balancer DNS name for backend API"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "ECS cluster name"
}

output "dynamodb_table_name" {
  value       = try(aws_dynamodb_table.sessions[0].name, "")
  description = "DynamoDB table name when using DynamoDB for sessions"
}

output "rds_endpoint" {
  value       = try(aws_db_instance.main[0].address, "")
  description = "RDS endpoint address when RDS is enabled"
}

output "secrets_manager_prefix" {
  value       = "${aws_secretsmanager_secret.sn_instance_url.name}, ${aws_secretsmanager_secret.sn_user.name}, ${aws_secretsmanager_secret.sn_pass.name}, ${aws_secretsmanager_secret.openai_api_key.name}"
  description = "Secrets Manager secret names created for ServiceNow/OpenAI credentials"
}
