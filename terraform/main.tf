# AMI da Amazon Linux
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# Bucket S3
resource "aws_s3_bucket" "documentos" {
  bucket = var.bucket_name

  tags = {
    Project    = var.project_name
    CostCenter = var.cost_center
    Name       = "bucket-dataset"
  }
}

# IAM Role para EC2
resource "aws_iam_role" "ec2_role" {
  name = "sprint7-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "inline_policy" {
  name = "sprint7-ec2-policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject"]
        Resource = "arn:aws:s3:::${var.bucket_name}/*"
      },
      {
        Effect = "Allow"
        Action = ["bedrock:*"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "sprint7-ec2-instance-profile"
  role = aws_iam_role.ec2_role.name
}

# Instância EC2
resource "aws_instance" "chatbot" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  vpc_security_group_ids = [aws_security_group.default.id]

  tags = {
    Name       = "sprint7-instance"
    Project    = var.project_name
    CostCenter = var.cost_center
  }

  volume_tags = {
    Name       = "sprint7-volume"
    Project    = var.project_name
    CostCenter = var.cost_center
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y python3 pip
              pip3 install boto3 langchain chromadb
              EOF
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/aws/ec2/sprint7"
  retention_in_days = 7
}
