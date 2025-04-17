output "instance_id" {
  description = "ID da instância EC2"
  value       = aws_instance.sprint7_instance.id
}

output "public_ip" {
  description = "Endereço IP público da EC2"
  value       = aws_instance.sprint7_instance.public_ip
}


output "s3_bucket_name" {
  description = "Nome do bucket S3 para os documentos jurídicos"
  value       = aws_s3_bucket.documentos.id
}


output "cloudwatch_log_group" {
  description = "Nome do grupo de logs no CloudWatch"
  value       = aws_cloudwatch_log_group.log_group.name
}

