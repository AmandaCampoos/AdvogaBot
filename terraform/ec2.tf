# Instância EC2 com ChromaDB configurado
resource "aws_instance" "sprint7_instance" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  vpc_security_group_ids = [aws_security_group.default.id]
  key_name               = aws_key_pair.sprint7_key.key_name

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
              yum install -y python3-pip git
              pip3 install boto3 langchain langchain-aws chromadb pypdf

              # Cria ponto de montagem e formata EBS (caso precise)
              mkfs -t xfs /dev/xvdf || true
              mkdir -p /mnt/chromadb
              mount /dev/xvdf /mnt/chromadb
              echo "/dev/xvdf /mnt/chromadb xfs defaults,nofail 0 2" >> /etc/fstab

              echo "Setup completo para ChromaDB" >> /var/log/user_data.log
              EOF
}

# CloudWatch Log Group para EC2
resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/aws/ec2/sprint7"
  retention_in_days = 7
}
