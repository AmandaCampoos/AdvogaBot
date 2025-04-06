output "instance_id" {
  description = "ID da instância EC2 criada"
  value       = aws_instance.chatbot.id
}

output "public_ip" {
  description = "IP público da instância EC2"
  value       = aws_instance.chatbot.public_ip
}

output "s3_bucket_name" {
  description = "Nome do bucket S3 para os documentos jurídicos"
  value       = aws_s3_bucket.documentos.id
}


output "cloudwatch_log_group" {
  description = "Nome do grupo de logs no CloudWatch"
  value       = aws_cloudwatch_log_group.log_group.name
}

