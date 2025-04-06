variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo da instância EC2"
  default     = "t2.micro"
}

variable "bucket_name" {
  description = "Nome do bucket S3"
  default     = "amanda-rag-bucket" 
}

variable "project_name" {
  description = "Nome do projeto"
  default     = "sprint7"
}

variable "cost_center" {
  description = "Centro de custo"
  default     = "aws-janeiro"
}
